'''
Created on 09 may 2018

@author: gnafu
'''

from flask import jsonify, request
from flask_restful import reqparse, Resource

from Database import get_db
from Utility import limit_int


# https://developer.github.com/v3/guides/traversing-with-pagination/
# https://developer.wordpress.org/rest-api/using-the-rest-api/pagination/
searchParser= reqparse.RequestParser()
searchParser.add_argument('orderBy').add_argument('page').add_argument('per_page').add_argument('tagId')

# TagsList
# shows a list of all the tags associated with a specific Vehicle, and lets you POST to add new vehicles
class Tag(Resource):
    def get(self, vehicle_id, tag_epc, user_id=None):
        
        print(tag_epc)
        
        try:
            int(vehicle_id)
        except ValueError: 
            return None # the input is not an integer
        
        args = searchParser.parse_args()

        conn = get_db()
        cur = conn.cursor()
        SQL = "SELECT epc FROM tags where epc = %s limit 1;" 
        data = (tag_epc,) # keep the comma to make it a tuple
        cur.execute(SQL, data) 
        # row = cur.fetchone()
        rows = cur.fetchall()
        if rows == None:
            print("There are no results for this query")
            rows = []
        
        columns = [desc[0] for desc in cur.description]
        result = []
        for row in rows:
            row = dict(zip(columns, row))
            result.append(row)

        conn.commit()
        cur.close()
        return jsonify(result)

    def post(self, vehicle_id, tag_epc, user_id=None):
        content = request.json
        print(content)
        
        _id = content.get('epc', 1)
                
        conn = get_db()
        cur = conn.cursor()
        
        SQL = "INSERT INTO tags (epc, vehicle_id) VALUES (%s, %s) RETURNING epc;" 
        data = (_id, vehicle_id )
        id_of_new_row = None
        error_message = ""        
        
        try:
            cur.execute(SQL, data) 
        except Exception as e:
            print(e)
            if hasattr(e, 'diag') and hasattr(e.diag, 'message_detail') :
                error_message = e.diag.message_detail
            else :
                error_message = "Database error" 
            conn.rollback()
        else:
            conn.commit()
            id_of_new_row = cur.fetchone()[0]        
        
        cur.close()
        
        # TODO : 409 Conflict if tagId already exists
        if id_of_new_row is None : return {"Error" : error_message}, 404
        
        return id_of_new_row, 201

    def delete(self, vehicle_id, tag_epc, user_id=None):
        
        print(vehicle_id)
          
        conn = get_db()
        cur = conn.cursor()
        
        SQL = "DELETE FROM tags WHERE epc = %s RETURNING epc;" 
        data = (tag_epc, )
        
        try:
            cur.execute(SQL, data) 
        except Exception as e:
            print(e)
            conn.rollback()
        else:
            conn.commit()
        
        cur.close()
        
        return {"Result": "Deleted"}, 204


# TagsList
# shows a list of all the tags associated with a specific Vehicle, and lets you POST to add new vehicles
class TagsList(Resource):
    def get(self, vehicle_id, user_id=None):
        
        try:
            int(vehicle_id)
        except ValueError: 
            return None # the input is not an integer
        
        args = searchParser.parse_args()

        conn = get_db()
        cur = conn.cursor()
        SQL = "SELECT epc FROM tags where vehicle_id = %s order by epc limit 50;" 
        data = (vehicle_id,) # keep the comma to make it a tuple
        cur.execute(SQL, data) 
        # row = cur.fetchone()
        rows = cur.fetchall()
        if rows == None:
            print("There are no results for this query")
            rows = []
        
        columns = [desc[0] for desc in cur.description]
        result = []
        for row in rows:
            row = dict(zip(columns, row))
            result.append(row)

        conn.commit()
        cur.close()
        return jsonify(result)

    def post(self, vehicle_id, user_id=None):
        content = request.json
        print(content)
        
        _id = content.get('epc', 1)
                
        conn = get_db()
        cur = conn.cursor()
        
        SQL = "INSERT INTO tags (epc, vehicle_id) VALUES (%s, %s) RETURNING epc;" 
        data = (_id, vehicle_id )
        id_of_new_row = None
        error_message = ""        
        
        try:
            cur.execute(SQL, data) 
        except Exception as e:
            print(e)
            if hasattr(e, 'diag') and hasattr(e.diag, 'message_detail') :
                error_message = e.diag.message_detail
            else :
                error_message = "Database error" 
            conn.rollback()
        else:
            conn.commit()
            id_of_new_row = cur.fetchone()[0]        
        
        cur.close()
        
        # TODO : 409 Conflict if tagId already exists
        if id_of_new_row is None : return {"Error" : error_message}, 404
        
        return id_of_new_row, 201

    def delete(self, tag_epc, user_id=None):
        content = request.json
        print(content)
        
        _id = content.get('epc', 1)
                
        conn = get_db()
        cur = conn.cursor()
        
        SQL = "DELETE FROM tags WHERE epc = %s RETURNING epc;" 
        data = (tag_epc, )
        
        try:
            cur.execute(SQL, data) 
        except Exception as e:
            print(e)
            conn.rollback()
        else:
            conn.commit()
        
        cur.close()
        
        
        return {"Result": "Deleted"}, 204