import json
import boto3
import traceback

def auto(event,context):
    
    # Function Logs
    Output = ""
    title = "EC2 Termination"
    try:
            
        # Event Input
        acc_name = event["queryStringParameters"]["account"]
        reg_name = event["queryStringParameters"]["region"]
        ip = event["queryStringParameters"]["ids"]
        img = event["queryStringParameters"]["image"]
            
        # EC2 Client
        client  = boto3.client('ec2',region_name = reg_name)
        
        # Instance Ids and Image Bool
        inst_ids = []
        if ip=='all' or ip=='All' or ip=='ALL':
            resp = client.describe_instances()
            for r in resp['Reservations']:
                for i in r['Instances']:
                    inst_ids.append(i['InstanceId'])
        else: inst_ids = ip.split(',')
        
        make_img = False
        if img=='yes' or img=='Yes' or img=='YES' or img=='true' or img=='True' or img=='TRUE': make_img = True
        
        # Final Input Check 
        Output += "<h4>Verify all Inputs</h4>"
        Output += "Account Name : "+acc_name+"<br>"
        Output += "Region Name : "+reg_name+"<br>"
        Output += "Instance Ids =  ["
        for i in inst_ids: Output += i + ", "
        Output += "]<br>"
    
    
        Output += "<h4>Starting Execution.... </h4>"
        
        # Performing Operations for each Instances
        for id in inst_ids:
            Output += "<hr>"
            Output += "Executing on "+id+ " <br><br>"
    
            try:
                # Delete On Termination for all Volumes
                Output += "Fetching Volume Details... <br>"
                resp = client.describe_instance_attribute(Attribute = 'blockDeviceMapping', InstanceId = id,)
                Device_mapping = [{ 'DeviceName' : i['DeviceName'], 'Ebs' : { 'DeleteOnTermination' : True, 'VolumeId' : i['Ebs']['VolumeId'] }, } for i in resp['BlockDeviceMappings']]
                Output += "Done <br><br>"
            except:
                Output += "<h4>[ERROR]</h4>" + traceback.format_exc() + "<br><br>"
                
            try:
                # Modifying Delete On Termination = True and DisableApiTermination = False
                Output += "Enabling Delete_On_Termiantion for Volumes.... <br>"
                client.modify_instance_attribute(InstanceId = id, BlockDeviceMappings = Device_mapping,)
                Output += "Done <br>"
                Output += "Diasabling Delete Protection.... <br>"
                client.modify_instance_attribute(InstanceId = id, DisableApiTermination={'Value':False},)
                Output += "Done <br><br>"
            except:
                Output += "<h4>[ERROR]</h4>" + traceback.format_exc() + "<br><br>"
                
                
            try:
                # Getting EIP params : Allocation ID and Association ID
                Output += "Checking for allocated EIP.... <br>"
                resp = client.describe_addresses(
                    Filters = [
                        {
                            'Name' : 'instance-id',
                            'Values' : [id,]
                        },
                    ],
                )
            except:
                Output += "<h4>[ERROR]</h4>" + traceback.format_exc() + "<br><br>"
                
            try:    
                # Checking whether it has a Elastic IP
                if(len(resp['Addresses'])!=0):
                    Allocation_ID = resp['Addresses'][0]['AllocationId']
                    Association_ID = resp['Addresses'][0]['AssociationId']
        
                    # Dissociating Addresses
                    Output += "EIP Found.<br> Dissociating EIP "+Association_ID+ ".... <br>"
                    client.disassociate_address(AssociationId=Association_ID)
                    Output += "Done <br>"
                    # Releasing EIP
                    Output += "Releasing EIP "+Allocation_ID+ ".... <br>"
                    client.release_address(AllocationId=Allocation_ID)
                    Output += "Done <br><br>"
                else: Output += "Not Found. Done <br><br>"
            except:
                Output += "<h4>[ERROR]</h4>" + traceback.format_exc() + "<br><br>"
                
            try:
                # Create an Image File
                if make_img:
                    Output += "Creating AMI Image.... <br>"
                    resp = client.create_image(
                        InstanceId = id,
                        Description = 'An AMI for deleted Instances',
                        Name = id+'_Automated_AMI',
                        NoReboot = True
                    )
                    Output += "Done. AMI ID : "+resp['ImageId']+ " <br><br>"
            except:
                Output += "<h4>[ERROR]</h4>" + traceback.format_exc() + "<br><br>"
            
            try:
                # Terminate Instances
                Output += "Terminating Instance "+id+ ".... <br>"
                client.terminate_instances(InstanceIds = [id,])
                Output += "Done <br>"
                Output += "<hr>"
            except:
                Output += "<h4>[ERROR]</h4>" + traceback.format_exc() + "<br>"
    except:
        Output += "<h4>[ERROR]</h4>" + traceback.format_exc() + "<br><br>"
    finally:
        Output += "<h4><br>Execution Finished. </h4>"
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

    
