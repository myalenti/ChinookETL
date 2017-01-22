'''
Created on Jan 9, 2017

@author: myalenti
'''
import mysql.connector
import decimal
from pymongo import MongoClient, results, version
import pymongo
from bson.decimal128 import Decimal128 
from bson.son import SON
from functools import total_ordering



def connMongo(coll):
    conn = MongoClient()
    col = conn['Chinook'][coll]
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
    conn = MongoClient()
    db = conn['Chinook']
    #x = db.command("buildinfo")
    #print x
    viewCommand = SON()
    viewCommand['create'] = "reduxCustomers"
    viewCommand['viewOn'] = "Customers"
    viewCommand['pipeline'] = [ { "$project" : { "name" : 0, "Contact.address" : 0 , "Contact.phone" : 0 , "Contact.fax" : 0 , "Contact.email" : 0 , "Contact.company" : 0 , "invoices.BillingAddress" : 0 }}]
    db.command(viewCommand)

mysqlUser="root"
mysqlPassword=""
mysqlHost=""
mysqlDatabase="Chinook"
myconn = mysql.connector.connect(user=mysqlUser,password=mysqlPassword,host=mysqlHost, database=mysqlDatabase)

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
query = ( "select iv.InvoiceId, iv.Trackid, iv.UnitPrice, iv.Quantity, t.Name, t.Composer from  InvoiceLine as iv, Track as t where iv.Trackid = t.TrackId;")
cursorDict = myconn.cursor(dictionary=True)
cursorDict.execute(query)
for record in cursorDict:
    unitPrice = record['UnitPrice']
    record['UnitPrice'] = Decimal128(unitPrice)
    updateTracksToMongo(record, record['InvoiceId'], "Customers" )
cursorDict.close()

myconn.close()
createRedactedView()
print "ETL Complete"

    
    