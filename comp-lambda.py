import logging
import pymysql
import json
import os
import boto3
from datetime import datetime, timedelta, time

# Logger settings - CloudWatch - this is needed in every function to enable logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
    
    # Connect to the RDS instance
    logger.info("Connecting to MySQL database")
    conn = pymysql.connect(host=os.environ['dev_db_host'], \
    port=int(os.environ['db_port']), user=os.environ['db_user'], \
    passwd=os.environ['dev_db_password'], \
    db=os.environ['db_name'],connect_timeout=3)
    logger.info("SUCCESS: Connection to MySQL database succeeded")
    
    sql_date = datetime.now().strftime("%Y-%m-%d")
    sql_time = datetime.now().strftime("%H:%M:%S")
    
    try:
        request_type = event["RequestType"]
        data_dict = event["DataDict"][0]
    except Exception:
        return {"statusCode":400, "errorMessage":"Not all variables passed, \
        required: RequestType and DataDict."}
        
    # function for executing SQL statements
    def execute_statement(statement):
        with conn.cursor() as cur:
            try:
                logger.debug(statement)
                cur.execute(statement)
                if statement[:6] == "SELECT":
                    results = cur.fetchall()
                    field_names =  [i[0] for i in cur.description]
                    conn.commit()
                    return (field_names, results)
                else:
                    conn.commit()
                    return
            except pymysql.Error as err:
                print(err)
                raise err
                
    try:
        if request_type == "ActiveDevices":
            field_names, results = execute_statement("SELECT d.DeviceID FROM \
            AWSPMS.Devices d WHERE d.CurrentActiveStatus='Active';")
            results = [i[0] for i in results]
            
            return {'statusCode': 200, 'field_names': field_names, 'Values':results}
            
        elif request_type == "LoadDeviceDates":
            field_names, results = execute_statement("SELECT \
            DATE_FORMAT(MIN(OutputDate), '%Y-%m-%d') AS 'MinOutputDate', \
            DATE_FORMAT(MAX(OutputDate), '%Y-%m-%d') AS 'MaxOutputDate' \
            FROM AWSPMS.CVOutput WHERE DeviceID='{}';"\
            .format(data_dict["DeviceID"]))
            
            reading_dates = execute_statement("SELECT \
            DISTINCT(DATE_FORMAT(OutputDate, '%Y-%m-%d')) AS 'OutputDate' \
            FROM AWSPMS.CVOutput WHERE DeviceID='{}';"\
            .format(data_dict["DeviceID"]))
            
            return {'statusCode': 200, 'field_names': field_names, 'Values':results, 'ReadingDates': [i[0] for i in reading_dates[1]]}
            
        elif request_type == "LoadCVReadingTimes":
            if data_dict["FirstDate"] == "" and data_dict["SecondDate"] == "":
                return {'statusCode':400, \
                "errorMessage": "FirstDate and SecondDate Value is an Empty String"}
                
            elif data_dict["FirstDate"] != "" and data_dict["SecondDate"] == "":
                first_date_data = execute_statement("SELECT \
                TIME_FORMAT(c.OutputTime,'%T') AS 'OutputTime' FROM \
                AWSPMS.CVOutput c WHERE c.DeviceID='{}' AND c.OutputDate='{}';"\
                .format(data_dict["DeviceID"], data_dict["FirstDate"]))[1]
                
                conn.close()
                return {'statusCode': 200, 'FirstDateReadings':first_date_data, \
                'SecondDateReadings':[]}
            
            else:
                first_date_data = execute_statement("SELECT \
                TIME_FORMAT(c.OutputTime,'%T') AS 'OutputTime' FROM \
                AWSPMS.CVOutput c WHERE c.DeviceID='{}' AND c.OutputDate='{}';"\
                .format(data_dict["DeviceID"], data_dict["FirstDate"]))[1]
                
                second_date_data = execute_statement("SELECT \
                TIME_FORMAT(c.OutputTime,'%T') AS 'OutputTime' FROM \
                AWSPMS.CVOutput c WHERE c.DeviceID='{}' AND c.OutputDate='{}';"\
                .format(data_dict["DeviceID"], data_dict["SecondDate"]))[1]
                
                conn.close()
                return {'statusCode': 200, 'FirstDateReadings':first_date_data, \
                'SecondDateReadings':second_date_data}
            
        elif request_type == "LoadCVData":
            s3 = boto3.client('s3', aws_access_key_id='********************', \
            aws_secret_access_key='*********************************')
            bucket = '**************'
            
            paginator = s3.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=bucket, \
            Prefix='{}/Device Readings/{}'\
            .format(data_dict["DeviceID"][:9], data_dict["ReadingDate"]))
            key = ""
            
            # loop through each page and get the objects in it
            for page in pages:
                if page["KeyCount"] != 0:
                    for i in range(len(page['Contents'])):
                        file_name = page['Contents'][i]["Key"]
                        file_entry_time = page['Contents'][i]["LastModified"].replace(tzinfo = None)
                        if data_dict["ReadingTime"] in file_name:
                            key = file_name
            
            logger.info(key)
            response = s3.get_object(Bucket=bucket, Key=key)
            content = response["Body"]
            read_file = content.read().decode('ascii')
            file_data = [read_file]
            
            for file in file_data:
                if data_dict["DeviceID"].endswith("B"):
                    cv = file[file.find("CV2")+6:]
                    bracket = cv.find(']}')
                    cv_data = cv[:bracket+1].split('], [')
                    cv_data[0] = cv_data[0][2:]
                    cv_data[1] = cv_data[1][:-2]
                    cv_data[0] = cv_data[0].split(', ')
                    cv_data[1] = cv_data[1].split(', ')
                else:
                    cv = file[file.find("CV")+5:]
                    bracket = cv.find(']]')
                    cv_data = cv[:bracket+1].split('], [')
                    cv_data[0] = cv_data[0][2:]
                    cv_data[1] = cv_data[1][:-1]
                    cv_data[0] = cv_data[0].split(', ')
                    cv_data[1] = cv_data[1].split(', ')
            
            voltage_list = []
            current_list = []
            for v in cv_data[0]:
                voltage_list.append(float(v))
            for c in cv_data[1]:
                current_list.append(float(c))
            
            return {'statusCode': 200, 'VoltageList': voltage_list, 'CurrentList':current_list}
            
        # elif request_type == "Remove":
            
        #     conn.close()
        #     return {'statusCode':200}
            
        else:
            return {'statusCode':400, \
            "errorMessage": "RequestType variable was incorrectly set."}
            
        conn.close()
        return {'statusCode': 200}
    
    except pymysql.Error as err:
        logger.debug(err)
        return ("Error: {}".format(err.args[0]),err.args[1])
    
    except Exception as e:
        logger.debug(e)
        return (400,e)