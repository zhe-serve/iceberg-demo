FROM apache/spark:3.5.3
USER root
RUN pip install pyspark google-auth[requests]

RUN curl -L "https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.9.1/iceberg-spark-runtime-3.5_2.12-1.9.1.jar" \
    -o /opt/spark/jars/iceberg-spark-runtime-3.5_2.12-1.9.1.jar && \
    curl -L "https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar" \
    -o /opt/spark/jars/gcs-connector-hadoop3-latest.jar

USER spark
