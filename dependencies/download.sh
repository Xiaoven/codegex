#!/bin/sh
wget -nc "https://repo1.maven.org/maven2/org/apache/ivy/ivy/2.5.0/ivy-2.5.0.jar" -P lib
java -jar lib/ivy-2.5.0.jar -ivy ivy.xml -retrieve 'jars/[artifact]-[revision](-[classifier]).[ext]'