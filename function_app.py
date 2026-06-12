import datetime
import logging
import os

import azure.functions as fap
from azure.storage.blob import BlobServiceClient

app = fap.FunctionApp()

CONTAINER_NAME = "fichiers-api"


@app.timer_trigger(
    schedule="0 */30 * * * *",
    arg_name="myTimer",
    run_on_startup=True,
    use_monitor=False
)
def clean_blob_storage(myTimer: fap.TimerRequest) -> None:
    logging.info("Début du nettoyage du Storage Account...")

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    if not connection_string:
        logging.error("Variable AZURE_STORAGE_CONNECTION_STRING manquante.")
        return

    max_age_minutes = int(os.getenv("MAX_BLOB_AGE_MINUTES", "5"))

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    now = datetime.datetime.now(datetime.timezone.utc)
    deleted_count = 0

    for blob in container_client.list_blobs():
        if blob.creation_time is None:
            logging.warning(f"Impossible de connaître la date de création de {blob.name}")
            continue

        age = now - blob.creation_time

        if age > datetime.timedelta(minutes=max_age_minutes):
            container_client.delete_blob(blob.name)
            deleted_count += 1
            logging.info(f"Blob supprimé : {blob.name}")

    logging.info(f"Nettoyage terminé. Nombre de fichiers supprimés : {deleted_count}")