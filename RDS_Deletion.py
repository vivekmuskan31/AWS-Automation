import json
import boto3
import traceback

def lambda_handler(event, context):
    Output = ""     # Function Log
    title = "RDS Deletion"
    try:
        # Event Input
        acc_name = event["queryStringParameters"]["account"]
        reg_name = event["queryStringParameters"]["region"]
        ip = event["queryStringParameters"]["ids"]
        ss = event["queryStringParameters"]["snapshot"]
        
        # # Test Inputs for Lambda
        # acc_name = "vivek"
        # reg_name = "us-east-1"]
        
        # ip = "all"
        # ss = "yes"
        
        # ELB v2.0 client
        client = boto3.client('rds',region_name = reg_name)
        
        # List of DB Identfires and Snapshot Bool
        db_ids = None
        if ip == 'all' or ip=='All' or ip=='ALL':
            resp = client.describe_db_instances()
            db_ids = [ i['DBInstanceIdentifier'] for i in resp['DBInstances'] ]
        else:
            db_ids = ip.split(',')
        
        take_snapshot = False
        if ss=="yes" or ss=="Yes" or ss=="YES" or ss=="true" or ss=="True" or ss=="TRUE": take_snapshot = True
        
        
        # Final Input Check
        Output += "<h4>Verify All Inputs</h4>Account Name : "+acc_name+"<br>Region : "+reg_name+"<br>Snapshot : "+ss+"<br>DB Ids : ["
        for d in db_ids: Output += d +", "
        Output += "] <br><h4>Execution Starting....</h4>"
        
        # Operating on each DB Instances
        for id in db_ids:
            Output += "<hr>"
            Output +=  "Operating on "+id+"<br><br>"
        
            # Modifying Deletion protection
            Output += "Disabling Deletion Protection...<br>"
            client.modify_db_instance(
                ApplyImmediately=True,
                DBInstanceIdentifier=id,
                DeletionProtection = False,
            )
            Output += "Done<br><br>"
        
            # Getting Parameter groups and Option groups
            Output += "Fetching Option and Paramter group names...<br>"
            resp = client.describe_db_instances(DBInstanceIdentifier = id,)
            param_gp_names = [ i['DBParameterGroupName'] for i in resp['DBInstances'][0]['DBParameterGroups']]
            option_gp_names = [ i['OptionGroupName'] for i in resp['DBInstances'][0]['OptionGroupMemberships']]
            Output += "Done<br><br>"
        
            # Deleting DB Instance
            Output += "Deleteing DB Instance...<br>"
            try:
                if take_snapshot:
                    client.delete_db_instance(
                        DBInstanceIdentifier=id,
                        SkipFinalSnapshot=False,
                        FinalDBSnapshotIdentifier=id+"AutomatedSnapshot",
                        DeleteAutomatedBackups=True
                    )
                else:
                    client.delete_db_instance(
                        DBInstanceIdentifier=id,
                        SkipFinalSnapshot=True,
                        DeleteAutomatedBackups=True
                    )
            except:
                Output += "<h4>[ERROR]</h4>" + traceback.format_exc() +"<br><br>"
            Output += "Done<br><br>"
        
            # Deleting Option Groups
            Output += "Deleting Option Groups...<br>"
            for o in option_gp_names:
                try:
                    client.delete_option_group(OptionGroupName = o,)
                except:
                    Output += "<h4>[ERROR]</h4>" + traceback.format_exc()+"<br>"
            Output += "Done<br><br>"
        
            # Deleting Parameter Groups
            Output += "Deleting Parameter Groups...<br>"
            for p in param_gp_names:
                try:
                    client.delete_db_parameter_group(DBParameterGroupName = p,)
                except:
                    Output += "<h4>[ERROR]</h4>" + traceback.format_exc()+"<br>"
            Output += "Done <br><br>"
        
            Output += "<hr>"
    
    except:
        Output += "<h4>[ERROR]</h4>" +traceback.format_exc() + "<br><br>"
    finally:
        Output += "<h4>Execution Finished</h4>"
    
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

    