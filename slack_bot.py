# pip install slack_bolt slack_sdk python-dotenv
# pip install aiohttp aiofiles
# 该程序为运行在服务器上的slack机器人，用于接收来自slack的文件上传请求，并进行处理，将处理结果发送回slack

import os
import logging
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import asyncio
import aiofiles
import aiohttp

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Slack app
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# Set to track processing PDFs
processing_pdfs = set()

# Synchronous function: Download file
def download_file(url, file_path):
    return asyncio.run(_download_file(url, file_path))

async def _download_file(url, file_path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"Authorization": f"Bearer {os.environ['SLACK_BOT_TOKEN']}"}) as response:
            if response.status == 200:
                async with aiofiles.open(file_path, mode='wb') as f:
                    await f.write(await response.read())
                logger.info(f"File downloaded: {file_path}")
                return True
            else:
                logger.error(f"File download failed: {response.status}")
                return False

# Synchronous function: Run run.py
def run_script():
    logger.info("Starting to run script...")
    result = asyncio.run(_run_script())
    logger.info(f"Script run result: {result}")
    return result

async def _run_script():
    current_dir = os.getcwd()
    logger.info(f"Current working directory: {current_dir}")
    
    process = await asyncio.create_subprocess_exec(
        'python3', 'run.py',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    if stdout:
        logger.info(f'[run.py] stdout:\n{stdout.decode()}')
    if stderr:
        logger.error(f'[run.py] stderr:\n{stderr.decode()}')
    
    if "GraphMaker2_png.py execution successful" in stdout.decode() or "GraphMaker2_png.py execution completed" in stdout.decode():
        return True
    return False

# Process file
def process_file(file_info, say):
    try:
        file_id = file_info["id"]
        file_name = file_info["name"]
        file_url = file_info["url_private_download"]
        
        # Safely get channel_id
        channel_id = None
        if "channels" in file_info and file_info["channels"]:
            channel_id = file_info["channels"][0]
        elif "ims" in file_info and file_info["ims"]:
            channel_id = file_info["ims"][0]
        
        if not channel_id:
            logger.error(f"Unable to determine channel_id: {file_info}")
            return

        if not file_name.lower().endswith('.pdf'):
            say(channel=channel_id, text="Please upload a PDF file.")
            return

        if file_name in processing_pdfs:
            say(channel=channel_id, text=f"File {file_name} is currently being processed. Please wait.")
            return

        processing_pdfs.add(file_name)

        input_pdf_path = 'input.pdf'

        download_success = download_file(file_url, input_pdf_path)
        if not download_success:
            say(channel=channel_id, text="File download failed. Please try again.")
            processing_pdfs.remove(file_name)
            return

        say(channel=channel_id, text=f"File {file_name} received. Starting processing...")

        try:
            run_success = run_script()
            if not run_success:
                say(channel=channel_id, text="An error occurred during processing. Please check the logs for more information.")
                processing_pdfs.remove(file_name)
                return
        except Exception as e:
            logger.error(f"Error running script: {str(e)}")
            say(channel=channel_id, text=f"An error occurred while running the script: {str(e)}")
            processing_pdfs.remove(file_name)
            return

        try:
            with open('output.txt', mode='r') as f:
                output_text = f.read()
            say(channel=channel_id, text=output_text)

            # Upload output file
            try:
                with open("output.txt", "rb") as file_content:
                    upload_result = app.client.files_upload_v2(
                        channels=file_info["channels"],
                        file=file_content,
                        filename="output.txt",
                        initial_comment="This is the text file of the processing result."
                    )
                logger.info(f"Text file upload successful: {upload_result}")
            except Exception as e:
                logger.error(f"Text file upload failed: {e}")

            # Upload image file
            try:
                with open("knowledge_graph.png", "rb") as file_content:
                    upload_result = app.client.files_upload_v2(
                        channels=file_info["channels"],
                        file=file_content,
                        filename="knowledge_graph.png",
                        initial_comment="This is the knowledge graph of the processing result."
                    )
                logger.info(f"Image file upload successful: {upload_result}")
            except Exception as e:
                logger.error(f"Image file upload failed: {e}")

            say(channel=channel_id, text="Processing complete!")

        except Exception as e:
            logger.error(f"Failed to send results: {str(e)}")
            say(channel=channel_id, text="Processing complete, but an error occurred while sending the results.")
            return

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        if channel_id:
            say(channel=channel_id, text=f"An error occurred while processing the file: {str(e)}")
    finally:
        if 'file_name' in locals():
            processing_pdfs.remove(file_name)

@app.event("file_created")
def handle_file_created(body, logger):
    logger.info(f"Received file_created event: {body}")
    event = body["event"]
    file_id = event.get("file_id")
    if file_id:
        try:
            file_info = app.client.files_info(file=file_id)["file"]
            process_file(file_info, app.client.chat_postMessage)
        except Exception as e:
            logger.error(f"Error processing file_created event: {e}")
    else:
        logger.warning("Received file_created event without file_id")

@app.event("file_shared")
def handle_file_shared(body, logger):
    logger.info(f"Received file_shared event: {body}")
    event = body["event"]
    file_id = event.get("file_id")
    channel_id = event.get("channel_id")
    if file_id:
        try:
            file_info = app.client.files_info(file=file_id)["file"]
            # Ensure file_info contains channel_id
            if "channels" not in file_info or not file_info["channels"]:
                file_info["channels"] = [channel_id]
            process_file(file_info, app.client.chat_postMessage)
        except Exception as e:
            logger.error(f"Error processing file_shared event: {e}")
    else:
        logger.warning("Received file_shared event without file_id")

@app.event("message")
def handle_message(event, say):
    if "files" not in event:
        say("Please send a PDF file directly.")

# Error handling
@app.error
def error_handler(error, body, logger):
    logger.error(f"Error: {error}")
    logger.error(f"Request body: {body}")

# Main function
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()

