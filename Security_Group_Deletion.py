import json
import boto3
import traceback

def deleteSG(sg_ids,client):
    function_logs=""
    for id in sg_ids:
        function_logs += "<hr>" 
        function_logs += "Operating On "+id['Name']+"<br><br>"
        
        # Getting Parameters for checking Inboounds
        try:
            resp = client.describe_security_groups(Filters = [{ 'Name' : 'ip-permission.group-id', 'Values' : [id['Id'],]},],)
        except:
            function_logs += "<h4>[ERROR]</h4>" + traceback.format_exc() + "<br><br>"
            
        else:
            # Checking Inbounds
            if len(resp['SecurityGroups'])!=0:
                
                # Getting List of SG whose Inbound is dependent
                Dependency = []
                for i in resp['SecurityGroups'] : Dependency.append({ 'Id' : i['GroupId'], 'Name' : i['GroupName']})
                function_logs += "[WARNING] : Dependency Found.<br>List of Dependencies = ["
                for i in Dependency: function_logs += i['Name'] + ", "
                function_logs += "]<br><br>"
                
                # Revoking Inbound Permissions
                try:
                    for sgid,sg in zip(Dependency,resp['SecurityGroups']):
                        permit = None
                        for permission in sg['IpPermissions']:
                            for User in permission['UserIdGroupPairs']:
                                if User['GroupId'] == id['Id']: 
                                    uid = User['UserId']
                                    permission['UserIdGroupPairs'] = [{'GroupId':id['Id'],'UserId': uid }]
                                    permit = permission
                                    break
                        # function_logs += "<h4> Permission Found </h4> Permits are : ["
                        # for p in permit['UserIdGroupPairs']: function_logs += p['GroupName']+", "
                        # function_logs += "]<br><br>"
                        # print(permit)
                        function_logs += "Revoking Inboound Rule of "+sgid['Name']+"....<br>"
                        client.revoke_security_group_ingress(
                            GroupId = sgid['Id'],
                            IpPermissions = [permit,],
                            DryRun = False
                        )
                        function_logs += "Done<br><br>"
                except:
                    function_logs += "<h4>[ERROR]</h4>" +traceback.format_exc()+"<br>"
            
        try:
            function_logs += "Deleting "+id['Name']+"....<br>"
            client.delete_security_group(GroupId=id['Id'])
        except:
            function_logs += "<h4>[ERROR]</h4>" + traceback.format_exc() + "<br><br>"
        else:
            function_logs += id['Name']+" Deleted.<br>"
        function_logs +=  "<hr>"
    return function_logs
    

def lambda_handler(event, context):
    
    # Function Logs
    Output = ""
    title = "Security Group Deletion"
    try:
        # Event Input
        acc_name = event["queryStringParameters"]["account"]
        reg_name = event["queryStringParameters"]["region"]
        ip = event["queryStringParameters"]["ids"]
        
        # # Test Input
        # acc_name = 'vivek'
        # reg_name = 'us-east-1'
        # ip = 'sg-04bd26380d8ea4359,sg-034cdf159c6e7e9e6'
        
        # EC2 Client
        client  = boto3.client('ec2',region_name = reg_name)
        
        
        # Instance Ids and Image Bool
        sg_ids = None
        if ip=='all' or ip=='All' or ip=='ALL':
            resp = client.describe_security_groups()
            sg_ids = [ { 'Id' : i['GroupId'], 'Name' : i['GroupName'] } for i in resp['SecurityGroups']]
        else:
            ids = ip.split(',')
            resp = client.describe_security_groups(GroupIds = ids)
            sg_ids = [ { 'Id' : i['GroupId'], 'Name' : i['GroupName'] } for i in resp['SecurityGroups']]
        
        # Final Input Check
        Output += "<h4>Verify all Inputs</h4>"
        Output += "Account Name : "+acc_name+"<br>"
        Output += "Region Name : "+reg_name+"<br>"
        Output += "SecurityGroup Ids =  ["
        for i in sg_ids: Output += i['Name'] + ", "
        Output += "]<br><br>"
        
        Output += "<h4>Starting Execution.... </h4>"
        Output += deleteSG(sg_ids,client)
        
    except:
        Output += "<h4>[ERROR]</h4>" + traceback.format_exc()+"<br>"
    finally:
        Output += "<h4>Execution Finished.</h4>"
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
            