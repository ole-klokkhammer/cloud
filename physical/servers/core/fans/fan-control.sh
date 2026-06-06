#!/bin/bash
# Temperature-based fan control for Supermicro + Noctua fans.
# Reads CPU temp via k10temp (EPYC), maps to PWM curve, applies via IPMI.
# Runs every 5 min via fan-speed.timer.
#
# Zone 0 = CPU/front fans, Zone 1 = peripheral/rear (+10% offset)
# Usage: fan-control.sh [BMC_IP] [USER] [PASS]

IPMI="ipmitool"

# Temp thresholds (°C, upper bound) and zone 0 PWM % at each step
THRESHOLDS=(35  45  55  65  75  999)
PWM_Z0=(    20  35  45  65  80  100)

get_max_temp() {
    local sdr cpu dimm max=0 val

    sdr=$($IPMI sdr type Temperature 2>/dev/null)

    # CPU Temp from IPMI (falls back to k10temp Tctl if missing)
    cpu=$(echo "$sdr" | grep -i "^CPU Temp" | head -1 | awk -F'|' '{print $5}' | tr -dc '0-9')
    if [[ -z "$cpu" || ! "$cpu" =~ ^[0-9]+$ ]]; then
        cpu=$(sensors k10temp-* 2>/dev/null \
            | grep -m1 'Tctl' \
            | awk '{print $2}' \
            | tr -d '+°C' \
            | cut -d. -f1)
    fi
    [[ "$cpu" =~ ^[0-9]+$ && $cpu -gt $max ]] && max=$cpu

    # Hottest DIMM bank (P1_DIMM* sensors, limit 85°C)
    while IFS= read -r line; do
        val=$(echo "$line" | awk -F'|' '{print $5}' | tr -dc '0-9')
        [[ "$val" =~ ^[0-9]+$ && $val -gt $max ]] && max=$val
    done < <(echo "$sdr" | grep -i "P1_DIMM")

    echo "${max:-50}"
}

set_pwm() {
    local zone=$1 pwm=$2 hex
    hex=$(printf '0x%02X' "$pwm")
    $IPMI raw 0x30 0x70 0x66 0x01 "$zone" "$hex"
}

TEMP=$(get_max_temp)
PWM0=100
for i in "${!THRESHOLDS[@]}"; do
    if [[ $TEMP -le ${THRESHOLDS[$i]} ]]; then
        PWM0=${PWM_Z0[$i]}
        break
    fi
done

PWM1=$(( PWM0 + 10 ))
(( PWM1 > 100 )) && PWM1=100

echo "CPU ${TEMP}°C → zone0=${PWM0}% zone1=${PWM1}%"
set_pwm 0 "$PWM0"
set_pwm 1 "$PWM1"
