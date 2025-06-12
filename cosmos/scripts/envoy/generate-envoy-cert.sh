#!/bin/bash

# Exit on error
set -e

# Cert file paths
CERT_DIR="./"
CERT_FILE="server.crt"
KEY_FILE="server.key"

# Java truststore path (default)
JAVA_CACERTS="${JAVA_HOME}/lib/security/cacerts"
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

echo "🔐 Importing cert into Java truststore at: ${JAVA_CACERTS}"
keytool -import -trustcacerts \
  -keystore "${JAVA_CACERTS}" \
  -storepass "${PASSWORD}" \
  -noprompt \
  -alias "${ALIAS}" \
  -file "${CERT_FILE}"

# Optional: import to hardcoded Java location (adjust if needed)
# ALT_CACERTS="/c/Program Files/Java/jdk-21/lib/security/cacerts"
# if [[ -f "${ALT_CACERTS}" ]]; then
#   echo "🔐 Also importing to alternate truststore at: ${ALT_CACERTS}"
#   keytool -import -trustcacerts \
#     -keystore "${ALT_CACERTS}" \
#     -storepass "${PASSWORD}" \
#     -noprompt \
#     -alias "${ALIAS}" \
#     -file "${CERT_FILE}"
# else
#   echo "⚠️  Alternate truststore path not found: ${ALT_CACERTS}"
# fi

echo "✅ Done."
