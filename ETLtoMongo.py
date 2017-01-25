#!/usr/bin/python
'''
Created on Jan 9, 2017

@author: myalenti
'''

#imports
import mysql.connector
import decimal
from pymongo import MongoClient, results, version
import pymongo
from bson.decimal128 import Decimal128 
from bson.son import SON
from functools import total_ordering
import getopt
import sys
import time

# functions
def usage():
    '''
    document
    '''
    print "python ETLtoMongo --mongoUri <mongodb://<ip>:<port> --mysqlIP <ip>"
    print ""
    
def connMongo(coll):
    conn = MongoClient(mongoUri)
    col = conn[mongoDB][coll]
    return col

def loadToMongo(someDict, coll):
    col = connMongo(coll)
    result = col.insert_one(someDict)
    #print result.inserted_id

def updateToMongo(someDict, customerId, coll):
    col = connMongo(coll)
    filter = { "_id" : customerId }
    result = col.update_one(filter, { "$addToSet" : { 'invoices' : someDict}})
    
def updateTracksToMongo(someDict, invoiceId, coll):
    col = connMongo(coll)
    filter = { "invoices.InvoiceId" : invoiceId }
    result = col.update_one(filter, { "$addToSet" : { 'tracks'  : someDict}})

def createRedactedView():
    print "Creating a view for redacted customer information"
    conn = MongoClient(mongoUri)
    db = conn[mongoDB]
    #x = db.command("buildinfo")
    #print x
    viewCommand = SON()
    viewCommand['create'] = "reduxCustomers"
    viewCommand['viewOn'] = "Customers"
    viewCommand['pipeline'] = [ { "$project" : { "name" : 0, "Contact.address" : 0 , "Contact.phone" : 0 , "Contact.fax" : 0 , "Contact.email" : 0 , "Contact.company" : 0 , "invoices.BillingAddress" : 0 }}]
    db.command(viewCommand)


if __name__ == '__main__':
    # executeMain()
    mysqlUser="root"
    mysqlPassword="password123!"
    mysqlHost="192.168.56.91"
    mysqlDatabase="Chinook"
    mongoUri = "mongodb://192.168.56.91:27017"
    mongoDB = "mongoChinook"
    tryConnect = True
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["mongoUri=", "mysqlIP="])
        
    except getopt.GetoptError:
        print "You provided invalid command line switches."
        usage()
        exit(2)
    
    for opt, arg in opts:
        #print "Tuple is " , opt, arg
        if opt in ("--mongoUri"):
            print "setting mongoUri to:" , arg
            mongoUri = str(arg)
        elif opt in ("--mysqlIP"):
            print "setting mysqlHost to:" , arg
            mysqlHost = str(arg)
        elif opt in ("-h"):
            usage()
            exit()
        else:
            usage()
            exit(2)
        
    print 'Attempting mysql connection: '    
    while tryConnect:
        sys.stdout.write('.')
        sys.stdout.flush()
        try:        
            myconn = mysql.connector.connect(user=mysqlUser,password=mysqlPassword,host=mysqlHost, database=mysqlDatabase)
            tryConnect = False
        except Exception:
            time.sleep(5)
            tryConnect = True 
    print "Connected"
    
    print "Using Version " + version
    ########## Moving the Employee Table####
    print ("Moving Employees as is. No schema refactoring - Its very Flat as is")
    query = ( "select * from Employee")
    cursorDict = myconn.cursor(dictionary=True)
    cursorDict.execute(query)
    for record in cursorDict:
        loadToMongo(record,"Employees")    
    cursorDict.close()
    #########
    
    ########Creating Customers#######
    print ("Moving Customers. Adding richness to the record")
    query = ( "select * from Customer")
    cursorDict = myconn.cursor(dictionary=True)
    cursorDict.execute(query)
    for record in cursorDict:
        newRecord = dict()    
        for key in record:
            newRecord['_id'] = record['CustomerId']
            newRecord['name'] = dict()
            newRecord['name']['firstName'] = record['FirstName']
            newRecord['name']['lastName'] = record['LastName']
            newRecord['Contact'] = dict()
            newRecord['Contact']['company'] = record['Company']
            newRecord['Contact']['address'] = record['Address']
            newRecord['Contact']['city'] = record['City']
            newRecord['Contact']['state'] = record['State']
            newRecord['Contact']['country'] = record['Country']
            newRecord['Contact']['postalCode'] = record['PostalCode']
            newRecord['Contact']['phone'] = record['Phone']
            newRecord['Contact']['fax'] = record['Fax']
            newRecord['Contact']['email'] = record['Email']
            newRecord['supportRepId'] = record['SupportRepId']
        loadToMongo(newRecord,"Customers")    
    cursorDict.close()
    
    ########Inserting Invoices to respective Customers#######
    print ("Inserting Invoices to Respective Customers.")
    print("Also creating an index on invoices.InvoiceId for future use")
    query = ( "select * from Invoice")
    
    result = connMongo("Customers").create_index([ ("invoices.InvoiceId" , pymongo.ASCENDING)] )
    cursorDict = myconn.cursor(dictionary=True)
    cursorDict.execute(query)
    for record in cursorDict:
        total = record['Total']
        record['Total'] = Decimal128(total)
        CustomerId = record['CustomerId']
        del record['CustomerId']
        updateToMongo(record, CustomerId, "Customers" )
    cursorDict.close()
    
    ########Inserting Tracks to each Invoice#######
    print ("Inserting Tracks to each Invoice.")
    print ("Also Creating a index for the track ID")
    result = connMongo("Customers").create_index([ ("tracks.Trackid" , pymongo.ASCENDING)] )
    #query = ( "select iv.InvoiceId, iv.Trackid, iv.UnitPrice, iv.Quantity, t.Name, t.Composer from InvoiceLine as iv, Track as t where iv.Trackid = t.TrackId;")
    query = ( "select iv.InvoiceId, iv.Trackid, iv.UnitPrice, iv.Quantity, t.Name, t.Composer, ar.Name as Artist, g.Name as genre, m.Name as MediaType, a.Title as Album from  InvoiceLine as iv, Track as t , Genre as g , MediaType as m , Album as a, Artist as ar where iv.Trackid = t.TrackId and t.GenreId = g.GenreId and t.MediaTypeId = m.MediaTypeId and t.AlbumId = a.AlbumId and a.ArtistId = ar.ArtistId;")
    cursorDict = myconn.cursor(dictionary=True)
    cursorDict.execute(query)
    for record in cursorDict:
        unitPrice = record['UnitPrice']
        record['UnitPrice'] = Decimal128(unitPrice)
        del record['Trackid']
        updateTracksToMongo(record, record['InvoiceId'], "Customers" )
    cursorDict.close()
    
    myconn.close()
    createRedactedView()
    print "ETL Complete"
    
