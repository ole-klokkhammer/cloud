# 


## sync
rsync -ahHAX --info=progress2 --partial --no-links   --exclude '**/node_modules/'   --exclude '**/build/'   --exclude '**/dist/' --exclude '**/.venv/' --exclude '**/venv/'    /home/ole/workspace/ /run/media/ole/79DD-D7E3/FILES/workspace/