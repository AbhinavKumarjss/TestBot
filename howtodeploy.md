## **Complete Elastic Beanstalk Deployment Guide**

### **Step 1: Create IAM Roles and Policies (Via AWS Console)**

#### **1.1 Create Service Role for Elastic Beanstalk**





1. **Go to IAM Console**
   * Search for "IAM" in AWS Console
   * Click on "IAM" service
2. **Create Service Role**
   * Click "Roles" in left sidebar
   * Click "Create role"
   * Select "AWS service" as trusted entity
   * Choose "Elastic Beanstalk" as service
   * Select "Elastic Beanstalk - Customizable" use case
   * Click "Next"
3. **Attach Policies**
   * Search and attach these policies:
     * `AWSElasticBeanstalkService`
     * `AWSElasticBeanstalkEnhancedHealth`
     * `AWSElasticBeanstalkManagedUpdatesCustomerRolePolicy`
   * Click "Next"
4. **Configure Role**
   * **Role name**: `GeneralChatbotElasticBeanstalkServiceRole`
   * **Description**: Service role for GeneralChatbot Elastic Beanstalk
   * Click "Create role"

#### **1.2 Create Instance Profile Role**





1. **Create Another Role**
   * Click "Create role" again
   * Select "AWS service" as trusted entity
   * Choose "EC2" as service
   * Select "Elastic Beanstalk - Customizable" use case
   * Click "Next"
2. **Attach Policies**
   * Search and attach these policies:
     * `AWSElasticBeanstalkWebTier`
     * `AWSElasticBeanstalkWorkerTier`
     * `AWSElasticBeanstalkMulticontainerDocker`
   * Click "Next"
3. **Configure Role**
   * **Role name**: `GeneralChatbotElasticBeanstalkEC2Role`
   * **Description**: EC2 instance role for GeneralChatbot
   * Click "Create role"
4. **Create Instance Profile**
   * Click on the created role
   * Go to "Trust relationships" tab
   * Click "Edit trust policy"
   * Replace with:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "Service": "ec2.amazonaws.com"
         },
         "Action": "sts:AssumeRole"
       }
     ]
   }
   ```
   * Click "Update trust policy"

#### **1.3 Create Custom Monitoring Policy**





1. **Create Policy**
   * Go to "Policies" in IAM
   * Click "Create policy"
   * Choose "JSON" tab
   * Paste this policy:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "CloudWatchLogs",
         "Effect": "Allow",
         "Action": [
           "logs:CreateLogGroup",
           "logs:CreateLogStream",
           "logs:PutLogEvents",
           "logs:DescribeLogGroups",
           "logs:DescribeLogStreams"
         ],
         "Resource": "*"
       },
       {
         "Sid": "CloudWatchMetrics",
         "Effect": "Allow",
         "Action": [
           "cloudwatch:PutMetricData",
           "cloudwatch:GetMetricData",
           "cloudwatch:ListMetrics"
         ],
         "Resource": "*"
       },
       {
         "Sid": "SystemsManager",
         "Effect": "Allow",
         "Action": [
           "ssm:GetParameter",
           "ssm:GetParameters",
           "ssm:GetParametersByPath"
         ],
         "Resource": "*"
       }
     ]
   }
   ```
2. **Save Policy**
   * **Policy name**: `GeneralChatbotMonitoringPolicy`
   * **Description**: Monitoring and logging permissions for GeneralChatbot
   * Click "Create policy"
3. **Attach to EC2 Role**
   * Go back to the `GeneralChatbotElasticBeanstalkEC2Role`
   * Click "Attach policies"
   * Search for `GeneralChatbotMonitoringPolicy`
   * Select it and click "Attach policy"

### **Step 2: Deploy to Elastic Beanstalk**

#### **2.1 Create Application**





1. **Go to Elastic Beanstalk Console**
   * Search for "Elastic Beanstalk" in AWS Console
   * Click on "Elastic Beanstalk" service
2. **Create Application**
   * Click "Create Application"
   * **Application name**: `GeneralChatbot`
   * **Description**: AI-Powered Conversational Assistant
   * Click "Create"

#### **2.2 Create Environment**





1. **Choose Environment Type**
   * Click "Create environment"
   * Select "Web server environment"
   * Click "Create"
2. **Configure Environment**

   ```
   Environment name: generalchatbot-prod
   Domain: [Leave as auto-generated]
   Platform: Python 3.11
   Platform branch: Python 3.11 running on 64bit Amazon Linux 2
   Platform version: Latest
   ```
3. **Configure Instance**

   ```
   Instance type: t3.medium
   Instance subnets: [Leave as default]
   ```

#### **2.3 Upload Application Code**





1. **Choose Source**
   * Select "Upload a file"
   * Click "Choose file"
   * Select your `GeneralChatbot-elasticbeanstalk.zip`
   * Click "Upload"

#### **2.4 Configure Environment Variables**





1. **Add Environment Properties**
   * Scroll down to "Environment properties"
   * Add these variables:

```
OPENAI_API_KEY = sk-proj-H30vwBURw4TJmZfvrEcXcDkfxoE8o2-ddpqDFzi-e4Evd5KygtUhks8rwZrXQMhZuE8rWr6Wt_T3BlbkFJy5wG96kVNNYOFdSkCPgDjUp7HaUXMAT_F8nQU8HXhg5eyGJ3RL9VNI5NnstWkM6oun2KJlMA

PINECONE_API_KEY = pcsk_3ERFN3_KtTcKvRRWPLUMRw3tAijQG4nxCv7zyYn2UYnfqhpWZauDiiGyZf9Q583CWLqLhx

ELEVEN_API_KEY = sk_681c5b0b20bec4e9948806833d18063721553711427efd11

PORT = 8000

HOST = 0.0.0.0

ENVIRONMENT = production

ALLOWED_ORIGINS = https://yourdomain.com,https://www.yourdomain.com,http://localhost:3000

VITE_WEBSOCKET_URL = wss://yourdomain.com/api/user/ws

VITE_SERVER_API_URL = https://yourdomain.com/api/admin
```

#### **2.5 Configure Additional Settings**





1. **Click "Edit" in Additional settings**
2. **Software Configuration**
   * Environment properties: \[Already configured above\]
3. **Instances Configuration**
   * Instance type: t3.medium
   * EC2 security groups: \[Leave as default\]
4. **Capacity Configuration**
   * Environment type: Single Instance (for development)
   * Load balancer type: Application Load Balancer (for production)
5. **Load Balancer Configuration**
   * Load balancer type: Application Load Balancer
   * Processes: \[Leave as default\]
6. **Security Configuration**
   * **Service role**: Select `GeneralChatbotElasticBeanstalkServiceRole`
   * **EC2 instance profile**: Select `GeneralChatbotElasticBeanstalkEC2Role`

#### **2.6 Deploy Application**





1. **Review Configuration**
   * Scroll to bottom
   * Review all settings
   * Click "Create environment"
2. **Monitor Deployment**
   * Watch the deployment progress
   * Expected time: 5-10 minutes

### **Step 3: Post-Deployment Configuration**

#### **3.1 Verify Deployment**





1. **Check Environment Status**
   * Look for "Health: OK" status
   * Status should be "Ready"
2. **Access Application**
   * Click on the environment URL
   * Test all features

#### **3.2 Configure Custom Domain (Optional)**





1. **Route 53 Setup**
   * Go to Route 53 Console
   * Create hosted zone for your domain
   * Create CNAME record pointing to your EB environment
2. **Update Environment Variables**
   * Go back to Elastic Beanstalk
   * Update domain URLs in environment variables

#### **3.3 Set Up Monitoring**





1. **CloudWatch Logs**
   * Go to CloudWatch Console
   * Check log groups for your application
   * Set up log retention policies
2. **CloudWatch Metrics**
   * View application metrics
   * Set up dashboards for monitoring
3. **Set Up Alarms**
   * Create CloudWatch alarms for:
     * CPU utilization
     * Memory usage
     * Application errors
     * Response time

### **Step 4: Testing and Validation**

#### **4.1 Test Application Features**





1. **Frontend Testing**
   * ✅ Application loads correctly
   * ✅ UI components work
   * ✅ Navigation functions
2. **Backend Testing**
   * ✅ API endpoints respond
   * ✅ WebSocket connections work
   * ✅ Voice functionality works
3. **Integration Testing**
   * ✅ Frontend-backend communication
   * ✅ Real-time features work
   * ✅ Error handling works

#### **4.2 Performance Testing**





1. **Load Testing**
   * Test with multiple concurrent users
   * Monitor response times
   * Check resource utilization
2. **Stress Testing**
   * Test application limits
   * Monitor error rates
   * Check recovery behavior

### **Step 5: Production Optimization**

#### **5.1 Security Hardening**





1. **SSL Certificate**
   * Request SSL certificate in Certificate Manager
   * Configure HTTPS for your domain
2. **Security Headers**
   * Verify security headers are set
   * Configure CORS properly

#### **5.2 Performance Optimization**





1. **Auto Scaling**
   * Configure auto scaling policies
   * Set up load balancer health checks
2. **Caching**
   * Configure CloudFront for static assets
   * Set up Redis for session caching

### **🔧 Troubleshooting Common Issues**

#### **Issue 1: Deployment Fails**

```
Solution:
1. Check deployment logs in EB console
2. Verify environment variables are set correctly
3. Check IAM roles are properly configured
4. Ensure all required files are in the zip
```

#### **Issue 2: Application Not Loading**

```
Solution:
1. Check environment health status
2. Review application logs
3. Verify Nginx configuration
4. Test health endpoint
```

#### **Issue 3: WebSocket Connection Issues**

```
Solution:
1. Verify WebSocket URL is correct
2. Check load balancer configuration
3. Ensure WebSocket upgrade headers are set
4. Test WebSocket endpoint manually
```

#### **Issue 4: Environment Variables Not Working**

```
Solution:
1. Verify all environment variables are set
2. Check variable names are correct
3. Restart environment if needed
4. Check application logs for errors
```

### **📊 Monitoring and Maintenance**

#### **Daily Monitoring**

* Check environment health
* Review application logs
* Monitor resource usage
* Check error rates

#### **Weekly Maintenance**

* Review performance metrics
* Update dependencies
* Check security patches
* Backup configuration

#### **Monthly Review**

* Analyze usage patterns
* Optimize resource allocation
* Review cost optimization
* Plan capacity scaling

Your GeneralChatbot application is now ready for production deployment on AWS Elastic Beanstalk with proper IAM roles, monitoring, and security configurations!