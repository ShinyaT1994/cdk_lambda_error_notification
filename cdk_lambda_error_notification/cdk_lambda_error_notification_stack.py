import os

from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_logs_destinations as logs_destinations,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
)
from constructs import Construct

class CdkLambdaErrorNotificationStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # エラーを引き起こすLambda関数を作成
        error_trigger_function = lambda_.Function(
            self,
            "ErrorTriggerFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            code=lambda_.Code.from_asset(
                os.path.join('lambda', 'error_trigger_function')
            ),
        )
        
        # メッセ―ジを出すSNS Topicを作成
        topic = sns.Topic(self, 'MyTopic')
        
        # Subscription追加
        subscription = topic.add_subscription(
            subscriptions.EmailSubscription('メールアドレス')
        )
        
        # エラーメッセージを出すLambda関数を作成
        publish_message_function = lambda_.Function(
            self,
            'PublishMessageFunction',
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler='lambda_function.lambda_handler',
            code=lambda_.Code.from_asset(
                os.path.join('lambda', 'publish_message_function')
            ),
            environment={
                'TOPIC_ARN': topic.topic_arn
            },
        )
        
        # lambdaに権限を付与
        topic.grant_publish(publish_message_function)
        
        # LogGroupのSubscription Filterを追加
        error_trigger_function.log_group.add_subscription_filter(
            'ErrorTriggerFunctionSubscriptionFilter',
            destination=logs_destinations.LambdaDestination(
                publish_message_function
            ),
            filter_pattern=logs.FilterPattern.any_term('ERROR'),
        )
        