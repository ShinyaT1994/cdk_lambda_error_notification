import json
import boto3
import os
import gzip
import base64

def lambda_handler(event, context):
    sns_client = boto3.client('sns')
    topic_arn = os.environ['TOPIC_ARN'] 
    
    # デコード
    decoded_event = base64.b64decode(event['awslogs']['data'])
    
    # バイナリに圧縮されているため展開
    decoded_event = json.loads(gzip.decompress(decoded_event))
    
    # SNS通知
    # 件名
    subject = f'Error in {decoded_event["logGroup"]}' 
    
    # 本文
    # 見やすいように成形
    message = f'Account:\t{decoded_event["owner"]}\nLogGroup:\t{decoded_event["logGroup"]}\nLogStream:\t{decoded_event["logStream"]}\n'
    for i, log_event in enumerate(decoded_event['logEvents']):
        message += f'\nLogEvent-{i + 1}\n'
        for key, value in log_event.items():
            message += f'\t{key}:\t{value}\n'
    
    # メール送信
    response = sns_client.publish(
        TopicArn = topic_arn,
        Subject = subject,
        Message = message
    )
    
    return {
        'statusCode': 200
    }