
#FROM gradle:7-jdk11 AS build
#COPY --chown=gradle:gradle . /home/gradle/src
#WORKDIR /home/gradle/src
#
#ARG GITHUB_USERNAME
#ARG GITHUB_TOKEN
#ENV GITHUB_USERNAME=$GITHUB_USERNAME
#ENV GITHUB_TOKEN=$GITHUB_TOKEN
#RUN /bin/bash -c "source ./.env && gradle shadowJar --no-daemon"

FROM openjdk:11
EXPOSE 8080:8080
RUN mkdir /app
#COPY --from=build /home/gradle/src/build/libs/*.jar /app/dyson-mqtt.jar
COPY ./build/libs/*.jar /app/dyson-mqtt.jar
ENTRYPOINT ["java", "-Xms2m", "-Xmx64m", "-jar", "/app/dyson-mqtt.jar"]