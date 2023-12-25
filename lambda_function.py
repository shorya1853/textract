import os
import boto3
from collections import defaultdict
from urllib.parse import unquote_plus
from PIL import Image
import pytesseract

tesseract_path = os.environ.get('TESSERACT_PATH', '/usr/local/bin/tesseract')
pytesseract.pytesseract.tesseract_cmd = tesseract_path


def has_lot_of_text(bucket, key):
    
    s3 = boto3.client('s3')
    
    # Download the image from S3
    download_path = 'filled_form.png'
    s3.download_file(bucket, key, download_path)
    
    img = Image.open(download_path)
    # Use Tesseract to do OCR on the image
    #text = pytesseract.image_to_string(img)
    text = pytesseract.image_to_string(img ,lang='eng', config='--psm 13 --tessdata-dir /root/tesseract-ocr/tessdata/ --oem 1 -c tessedit_char_whitelist=ABCDEFG0123456789')
    # Check if the extracted text is not empty
    
    return bool(text.strip())
    

def get_kv_map(bucket, key):
    # process using image bytes
    client = boto3.client('textract')
    response = client.analyze_document(Document={'S3Object': {'Bucket': bucket, "Name": key}}, FeatureTypes=['FORMS'])

    # Get the text blocks
    blocks = response['Blocks']
    print(f'BLOCKS: {blocks}')

    # get key and value maps
    key_map = {}
    value_map = {}
    block_map = {}
    for block in blocks:
        block_id = block['Id']
        block_map[block_id] = block
        if block['BlockType'] == "KEY_VALUE_SET":
            if 'KEY' in block['EntityTypes']:
                key_map[block_id] = block
            else:
                value_map[block_id] = block

    return key_map, value_map, block_map


def get_kv_relationship(key_map, value_map, block_map):
    kvs = defaultdict(list)
    for block_id, key_block in key_map.items():
        value_block = find_value_block(key_block, value_map)
        key = get_text(key_block, block_map)
        val = get_text(value_block, block_map)
        kvs[key].append(val)
    return kvs


def find_value_block(key_block, value_map):
    for relationship in key_block['Relationships']:
        if relationship['Type'] == 'VALUE':
            for value_id in relationship['Ids']:
                value_block = value_map[value_id]
    return value_block


def get_text(result, blocks_map):
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    word = blocks_map[child_id]
                    if word['BlockType'] == 'WORD':
                        text += word['Text'] + ' '
                    if word['BlockType'] == 'SELECTION_ELEMENT':
                        if word['SelectionStatus'] == 'SELECTED':
                            text += 'X'

    return text

def lambda_handler(event, context):

    file_obj = event["Records"][0]
    
    bucket = unquote_plus(str(file_obj["s3"]["bucket"]["name"]))
    #file_name = unquote_plus(str(file_obj["s3"]["object"]["key"]))
    file_name ='filled_form.png'
    print(f'Bucket: {bucket}, file: {file_name}')
    if has_lot_of_text(bucket, file_name):
        key_map, value_map, block_map = get_kv_map( bucket, file_name)

        # Get Key Value relationship
        kvs = get_kv_relationship(key_map, value_map, block_map)
        print("\n\n== FOUND KEY : VALUE pairs ===\n")

        for key, value in kvs.items():
            print(key, ":", value)

# lambda_handler({
#     "Records": [
#         {
#             "eventVersion": "2.1",
#             "eventSource": "aws:s3",
#             "awsRegion": "ap-south-1",
#             "eventTime": "2023-12-22T11:38:20.038Z",
#             "eventName": "ObjectCreated:Put",
#             "userIdentity": {
#                 "principalId": "AWS:AIDA5AFK32U7VKGK2FH62"
#             },
#             "requestParameters": {
#                 "sourceIPAddress": "49.43.24.193"
#             },
#             "responseElements": {
#                 "x-amz-request-id": "Q1CBGW2F1KJZ5N85",
#                 "x-amz-id-2": "M0Y9HxsgZbvd9kbdR3t98RHMgeXNxiD8O8DT3LkqZMpDaq3rkTda6bFgZtzZQW1ft59mM002/NgQWA5eWNsmAPrjNZJ7oJyI"
#             },
#             "s3": {
#                 "s3SchemaVersion": "1.0",
#                 "configurationId": "2635c4db-9c1d-49c3-855b-7bcb8931436e",
#                 "bucket": {
#                     "name": "csvconverted123",
#                     "ownerIdentity": {
#                         "principalId": "A3U8MDLYZJ18I1"
#                     },
#                     "arn": "arn:aws:s3:::csvconverted123"
#                 },
#                 "object": {
#                     "key": "filled_form.png",
#                     "size": 797532,
#                     "eTag": "0e3bc8100e218137e42d41eaaa7688c8",
#                     "sequencer": "006585752BF39657E1"
#                 }
#             }
#         }
#     ]
# }, 1)