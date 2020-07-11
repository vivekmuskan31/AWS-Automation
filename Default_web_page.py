import json

def lambda_handler(event, context):
    # TODO implement
    Output = "This message is autogenrated<br>This should be in newline"
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
            <title> AWS Deletion Console</title>

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


        <!--Main Content and Body-->
        <body>
            
            <!--Title-->
            <header id="main-header">
                <h1> Welcome to Automated AWS Deletion Console</h1>
            </header>

            <section>
                <article>
                    <p>
                        This console provides you cost effective deletion of unused AWS Services.
                        It also provides flexiblities such as creating image of EC2 instances or 
                        taking final snapshot of RDS. It automatically check whether targets are
                        attached to Load Balancers and also remove security groups from inbounds of other
                        security groups before deleting it.
                    </p>
                </article>
            </section>
            <br>
            <h3> Home Page/Default Page Link : <em><u>http://lamdaapi-1599659077.us-east-2.elb.amazonaws.com</u></em></h3>
            <a href="https://drive.google.com/drive/folders/1Ig2Cxned7CXezlnEHHE0hrjjG262UK3h" target="_blank">Click here for detailed documentation and complete scripts</a>
            <br>
            <h2> Available Services : </h2>
            <p>
                <table style="width:1400px">
                    <thead>
                        <tr>
                            <th><h3><strong>Services</strong></h3></th>
                            <th><h3><strong>Path</strong></h3></th>
                            <th><h3><strong>Inputs</strong></h3></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>1. EC2 Termination</strong></td>
                            <td>/ec2terminate</td>
                            <td>?account=<em>ACCOUNT_NAME</em>&ampregion=<em>REGION_NAME</em>&ids=<em>INSTANCE_IDS</em>&image=<em>TRUE</em></td>
                        </tr>

                        <tr>
                            <td><strong>2. RDS Deletion</strong></td>
                            <td>/rdsdelete</td>
                            <td>?account=<em>ACCOUNT_NAME</em>&ampregion=<em>REGION_NAME</em>&ids=<em>DB_IDS</em>&snapshot=<em>TRUE</em></td>
                        </tr>

                        <tr>
                            <td><strong>3. ALB Deletion</strong></td>
                            <td>/albdelete</td>
                            <td>?account=<em>ACCOUNT_NAME</em>&ampregion=<em>REGION_NAME</em>&ids=<em>ALB_ARNS</em></td>
                        </tr>

                        <tr>
                            <td><strong>4. ELB Deletion</strong></td>
                            <td>/elbdelete</td>
                            <td>?account=<em>ACCOUNT_NAME</em>&ampregion=<em>REGION_NAME</em>&ids=<em>ELB_NAMES</em></td>
                        </tr>

                        <tr>
                            <td><strong>5. Security Groups Deletion</strong></td>
                            <td>/sgdelete</td>
                            <td>?account=<em>ACCOUNT_NAME</em>&ampregion=<em>REGION_NAME</em>&ids=<em>SECURITY_GROUP_IDS</em></td>
                        </tr>

                        <tr>
                            <td><strong>6. CF Stacks Deletion</strong></td>
                            <td>/cfdelete</td>
                            <td>?account=<em>ACCOUNT_NAME</em>&ampregion=<em>REGION_NAME</em>&ids=<em>STACK_IDS</em></td>
                        </tr>
                        
                    </tbody>
                </table>
            </p>
            <section>
                <article>
                    <h3>Inputs</h3>
                    <ul>
                        <li><em>account</em> : Account Name of AWS Services (Eg : vivek OR himanshu)</li>
                        <li><em>region</em> : Region in which you want to delete (Eg : us-east-1 OR us-west-2)</li>
                        <li><em>ids</em> : Commas separeted IDs/Names of Instance/LB/SG/Stack OR <em>all</em> if you want to delete all of them
                        (Eg : i-347cff458745,i-34809jg093)</li>
                        <li><em>image</em> : Whether you want to create image of EC2 Instance (Eg : True OR False)</li>
                        <li><em>snapshot</em> : Whether you want to take snapshot of DB Instance (Eg : True OR False)</li>
                        
                    </ul>
                </article>
                <article>
                    <h3>Example</h3>
                    <ol>
                    <li>EC2 Termination : <em><u>http://lamdaapi-1599659077.us-east-2.elb.amazonaws.com/ec2terminate?account=vivek&ampregion=us-east-1&ids=i-735c8389bf88,i-784c833ac38&image=False</u></em></li>
                    <br>
                    <li>RDS Deletion : <em><u>http://lamdaapi-1599659077.us-east-2.elb.amazonaws.com/rdsdelete?account=vivek&ampregion=us-east-1&ids=myDBtest1,myDBtest2&snapshot=False</u></em></li>
                    <br>
                    <li>ALB Deletion : <em><u>http://lamdaapi-1599659077.us-east-2.elb.amazonaws.com/albdelete?account=vivek&ampregion=us-east-1&ids=all</u></em></li>
                    <br>
                    <li>ELB Deletion : <em><u>http://lamdaapi-1599659077.us-east-2.elb.amazonaws.com/elbdelete?account=vivek&ampregion=us-east-1&ids=myLoadBalancer1,myLoadBalancer2</u></em></li>
                    <br>
                    <li>Security Group Deletion : <em><u>http://lamdaapi-1599659077.us-east-2.elb.amazonaws.com/sgdelete?account=vivek&ampregion=us-east-1&ids=sg-903004f8,sg-283e72a2</u></em></li>
                    <br>
                    <li>CF Stack Deletion : <em><u>http://lamdaapi-1599659077.us-east-2.elb.amazonaws.com/cfdelete?account=vivek&ampregion=us-east-1&ids=myLampStack,myRubyStack</u></em></li> 
                    </ol>
                </article>
            </section>
            
            <footer id="main-footer">
                <h4>Designed By : Vivek Muskan</h4>
            </footer>
        </body>
    </html>
    """
    return response
