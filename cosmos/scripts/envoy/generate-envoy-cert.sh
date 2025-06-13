#!/bin/bash

# Exit on error
set -e

# Cert file paths
CERT_DIR="./"
CERT_FILE="server.crt"
KEY_FILE="server.key"

# Java truststore path (default)
JAVA_CACERTS1="/usr/lib/jvm/default-java/lib/security/cacerts"
JAVA_CACERTS2="/usr/lib/jvm/java-11-openjdk-amd64/lib/security/cacerts"
JAVA_CACERTS3="/usr/lib/jvm/java-1.11.0-openjdk-amd64/lib/security/cacerts"
ALIAS="localhostcert"
PASSWORD="changeit"

echo "🔧 Generating self-signed certificate for CN=localhost..."
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout "${KEY_FILE}" \
  -out "${CERT_FILE}" \
  -subj "/CN=localhost"

chmod 777 "${CERT_FILE}" "${KEY_FILE}"
echo "✅ Certificate and key created with 777 permissions."

echo "🔐 Importing cert into Java truststore at: ${JAVA_CACERTS1}"
sudo keytool -import -trustcacerts \
  -keystore "${JAVA_CACERTS1}" \
  -storepass "${PASSWORD}" \
  -noprompt \
  -alias "${ALIAS}" \
  -file "${CERT_FILE}"

echo "🔐 Importing cert into Java truststore at: ${JAVA_CACERTS2}"

sudo keytool -import -trustcacerts \
  -keystore "${JAVA_CACERTS2}" \
  -storepass "${PASSWORD}" \
  -noprompt \
  -alias "${ALIAS}" \
  -file "${CERT_FILE}"

echo "🔐 Importing cert into Java truststore at: ${JAVA_CACERTS3}"

sudo keytool -import -trustcacerts \
  -keystore "${JAVA_CACERTS3}" \
  -storepass "${PASSWORD}" \
  -noprompt \
  -alias "${ALIAS}" \
  -file "${CERT_FILE}"

echo "✅ Done."