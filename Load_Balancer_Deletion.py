import json
import boto3
import traceback
def deleteALB(e_arns,reg_name):
    
    # ELB v2.0 client
    client = boto3.client('elbv2',region_name = reg_name)
    
    function_log = ""
    function_log += "<hr>"
    function_log += "Operating on "+e_arns['NAME']+"<br><br>"


    # Extracting all Target Groups Arn
    function_log += "Fetching Target Groups....<br>"
    resp_tg = client.describe_target_groups(LoadBalancerArn = e_arns['ARN'],)
    tg_Arns = [{'ARN' : i['TargetGroupArn'], 'NAME' : i['TargetGroupName']}  for i in resp_tg['TargetGroups']]
    function_log += "Done.Target Groups are : ["
    for i in tg_Arns:function_log += i['NAME']+", "
    function_log += "]<br><br>"


    # Extracting Registered Targets if any for all Target Groups
    function_log += "Checking Target Groups for registered Targets....<br>"
    for t_arn in tg_Arns:
        resp = client.describe_target_health(TargetGroupArn = t_arn['ARN'],)
        if len(resp['TargetHealthDescriptions']) != 0:
            function_log += "Target Found.<br><strong>[WARNING]</strong> : CANNOT Delete LB "+e_arns['NAME']
            function_log += "<br><strong>[DESCRIPTION] </strong>: "
            tgt_id = [ i['Target']['Id'] for i in resp['TargetHealthDescriptions']]
            function_log += "TARGETS [ "
            for t in tgt_id: function_log += t + ", "
            function_log += "] are attached to TARGET GROUP "+ t_arn['NAME']+ "<br><br>"
            function_log += "<hr>"
            return function_log
    function_log += "Done<br><br>"


    # Deleting All Listeners
    function_log += "Deleting Listeners....<br>"
    resp = client.describe_listeners(LoadBalancerArn = e_arns['ARN'],)
    ln_arns = [i['ListenerArn'] for i in resp['Listeners']]
    for l_arn in ln_arns: client.delete_listener(ListenerArn = l_arn,)
    function_log += "Done<br><br>"


    # Deleting Target Group with No registered Target
    function_log += "Deleting Target Groups....<br>"
    for t_arn in tg_Arns: client.delete_target_group(TargetGroupArn = t_arn['ARN'],)
    function_log += "Done<br><br>"

    # Disabling Delete Protection
    function_log += "Disabling Delete_Protection....<br>"
    client.modify_load_balancer_attributes(
        LoadBalancerArn = e_arns['ARN'],
        Attributes = [
            {
                'Key': 'deletion_protection.enabled',
                'Value' : 'false'
            },
        ]
    )
    function_log += "Done<br><br>"
    
    
    # Deleting Load Balancer
    function_log += "Deleting ELB"+e_arns['NAME']+"....<br>"
    client.delete_load_balancer(LoadBalancerArn = e_arns['ARN'])
    function_log += "Done<br>"
    function_log += "<hr>"
    
    return function_log
    
#############################################################################################################################################################################    
    
def deleteELB(elb_names,client):
    function_log = ""
    for id in elb_names:
        function_log += "<hr>"
        function_log += "Operating on " + id+"<br><br>"
        
        # Check For Instances
        function_log += "Fetching Target Details....<br>"
        try:
            resp = client.describe_instance_health(LoadBalancerName=id,)
        except:
            function_log += "<h4>[ERROR]</h4>" + traceback.format_exc() + "<br><br>"
        else:
            
            if len(resp['InstanceStates']) != 0:
                function_log += "<strong>[WARNING]</strong> : CANNOT Delete "+id+".<br><strong>[DESCRIPTION]</strong>: Instances [ "
                registered_ec2 = [{'InstanceId' : i['InstanceId']} for i in resp['InstanceStates']]
                for i in registered_ec2: function_log += i['InstanceId'] +", "
                function_log += "] are attached to LB "+id+".<br>"
                
            else:
                try:
                    function_log += "Deleting ELB "+id+"....<br>"
                    client.delete_load_balancer(LoadBalancerName=id,)
                except:
                    function_log += "<h4>[ERROR]</h4>" + traceback.format_exc() + "<br><br>"
                else:
                    function_log += "Done<br>"
        function_log += "<hr>"
         
    return function_log
    

#################################################################################################################################################################

def lambda_handler(event, context):
    
    Output = "" # Function Log
    title = "Load Balancer Deletion"
    try:
        # Event Input
        acc_name = event["queryStringParameters"]["account"]
        reg_name = event["queryStringParameters"]["region"]
        ip = event["queryStringParameters"]["ids"]
        
        
        # # Test Inputs for Lambda
        # acc_name = "vivek"
        # reg_name = "us-east-1"
        # ip = "all"
        
        # ELB vs ALB based on Path
        path = event["path"]
        isELB = False
        
        if path == "/elbdelete":
            isELB = True
            
            # ELB v1.0 client
            client = boto3.client('elb',region_name = reg_name)
            
            # Names of ELB
            elb_names = None
            if ip=='all' or ip=='All' or ip=='ALL':
                resp = client.describe_load_balancers()
                elb_names = [ i['LoadBalancerName'] for i in resp['LoadBalancerDescriptions']]
            else:
                elb_names = ip.split(',')
            
        else:
            
            # ELB v2.0 client
            client = boto3.client('elbv2',region_name = reg_name)
            
            # Arn List of Load Balancers
            elb_Arns = None
            if ip=='all' or ip=='All' or ip=='ALL':
                resp = client.describe_load_balancers()
                elb_Arns = [{'ARN' : i['LoadBalancerArn'], 'NAME' : i['LoadBalancerName']} for i in resp['LoadBalancers']]
        
            else:
                elbs = ip.split(',')
                resp = client.describe_load_balancers(LoadBalancerArns = elbs,)
                elb_Arns = [{'ARN' : i['LoadBalancerArn'], 'NAME' : i['LoadBalancerName']} for i in resp['LoadBalancers']]
    
        
    
        # Final Input Check
        Output += "<h4>Verify All Inputs </h4>Account Name : "+acc_name+"<br>Region : "+reg_name+"<br>LB Names : ["
        if isELB: 
            for e in elb_names: Output += e +", "
        else: 
            for e in elb_Arns: Output += e['NAME']+", "
        Output += "] <br> <h4>Execution Starting....</h4>"
        
        # Calling Function
        if isELB: Output += deleteELB(elb_names, client)
        else:
            for e_arns in elb_Arns: Output += deleteALB(e_arns, reg_name)
        
        
    except:
        Output += "<h4>[ERROR]</h4>"  + traceback.format_exc() + "<br><br"
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
    
    