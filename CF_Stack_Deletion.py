import json
import boto3
import traceback


def lambda_handler(event, context):
    
    # Function Logs
    Output = ""
    title = "CF Stack Deletion"
    try:
        # Event Input
        acc_name = event["queryStringParameters"]["account"]
        reg_name = event["queryStringParameters"]["region"]
        ip = event["queryStringParameters"]["ids"]
        
         
        # # Test Inputs for Lambda
        # acc_name = "vivek"
        # reg_name = "us-easXXXX"
        # ip = "all"
        
        # CloudFormation Client
        client = boto3.client('cloudformation',region_name = reg_name)
        
        # List of stack IDs
        stack_ids = None
        if ip == 'all' or ip=='All' or ip=='ALL':
            resp = client.describe_stacks()
            stack_ids = [ i['StackName'] for i in resp['Stacks'] ]
        else:
            stack_ids = ip.split(',')
        
        # Final Input Check
        Output += "<h4>Verify All Inputs</h4>Account Name : "+acc_name+"<br>Region : "+reg_name+"<br>Stack Ids : ["
        for s in stack_ids: Output += s +", "
        Output += "]<br> <h4> Execution Starting....</h4>"
        
        # Operating on each Stack
        for id in stack_ids:
            Output += "<hr>"
            Output +=  "Operating on "+id+"<br><br>"
        
            # Modifying Deletion protection
            Output += "Disabling Termination Protection...<br>"
            client.update_termination_protection(EnableTerminationProtection=False, StackName=id)
            Output += "Done<br><br>"
            
            Output += "Deleting "+id+"....<br>"
            try: 
                client.delete_stack(StackName=id)
            except:
                Output += "<h4> [ERROR]</h4>" + traceback.format_exc() + "<br><br>"
            else:
                Output += "Done<br><br>"
            
            Output += "<hr>"

    except:
        Output += "<h4> [ERROR]</h4>" + traceback.format_exc() + "<br><br>"
    finally:
        Output += "<h4>Execution Finished</h4>"
    ###############################################
    response = {
        "statusCode" : 200,
        "isBase64Encoded" : False,
        "headers" : {
            "Content-Type" : "text/html; charset=utf-8"
        }
    }
    response["body"] = """
    <!DOCTYPE html>
    <html>
        <!--Doesn't Show on Page-->
        <head>
            <!--Show as Title on tab-->
            <title> """ + title + """ </title>

            <!--Formatting and Style of Text-->
            <style>
                #main-header{
                    text-align:center;
                    background-color:lightyellow;
                    color:darkorange;
                    padding:30px;
                }

                #main-footer{
                    text-align:center;
                    font-size: 18px;
                }

            </style>
        </head>

        <body>
            <header id="main-header">
                <h1> Welcome to """ + title + """ Console </h1>
            </header>
            <br>
            <h2> Backend Server Logs : </h2>
            <br>
            """ + Output + """
            
            <footer id="main-footer">
                <h4>Designed By : Vivek Muskan</h4>
            </footer>
        </body>
    </html>
    """
    return response