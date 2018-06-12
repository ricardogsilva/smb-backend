'''
Created on 13 apr 2018

@author: gnafu
'''

from flask import jsonify, request, json
from flask_restful import reqparse, Resource

from Database import get_db, TABLE_NAMES, sql
from Utility import limit_int

searchParser= reqparse.RequestParser()
searchParser.add_argument('orderBy').add_argument('page').add_argument('per_page').add_argument('tagId').add_argument('dump')

# UsersList
# shows a list of all users, and lets you POST to add new users
class UsersList(Resource):
    def get(self):
        args = searchParser.parse_args()
         
        per_page = 50;
        offset = 0;
        dump = False;
        
        if args['per_page'] is not None:
            try:
                per_page=limit_int(int(args['per_page']), 0, 100)
            except ValueError: 
                pass
        
        if args['page'] is not None:
            try:
                offset=limit_int(int(args['page']) * per_page, 0)
            except ValueError: 
                pass
        
        if args['dump'] is not None:
            if args['dump'] == 'true':
                dump = True 

        print("DUMP is "+str(dump))        

        conn = get_db()
        cur = conn.cursor()
        
        SQL="SELECT * FROM {} order by id limit %s offset %s;"
        SQL = sql.SQL(SQL).format(sql.Identifier(TABLE_NAMES['users']))
        data = (per_page, offset)

        # if dump is true compose all users/vehicles/tags and output them
        if dump:
            SQL="SELECT * FROM {} order by id asc;"
            SQL = sql.SQL(SQL).format(sql.Identifier(TABLE_NAMES['users']))
            data = None
        
        
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

        
        if dump:
            for i in result:
                i['vehicles'] = []
                print(json.dumps(i))
                SQL="""Select v.id, v.lastupdate, v.type, v.name, v.status, v.image, v.owner, 
                            CASE WHEN ll.lastpos IS NOT NULL THEN
                                jsonb_build_object(
                                    'type',       'Feature',
                                    'id',         ll.gid,
                                    'geometry',   ST_AsGeoJSON(ll.lastpos)::jsonb,
                                    'properties', CASE WHEN ll.reporter IS NOT NULL THEN  json_build_object(
                                                                                            'reporter', ll.reporter
                                                                                         ) ELSE '{{}}' END
                                )
                                ELSE NULL
                            END as lastposition 
                            FROM {} as v LEFT JOIN 
                            (
                            SELECT d1.vehicle_id, d1.the_geom as lastpos, d1._id as gid, d1.reporter
                            FROM {} d1
                            LEFT JOIN {} d2 ON d1.vehicle_id = d2.vehicle_id AND coalesce(d1.timestamp, 0) < d2.timestamp
                            WHERE d2.timestamp IS NULL
                            ) as ll
                            on v._id = ll.vehicle_id
                        WHERE owner = %s order by id asc;"""
                SQL = sql.SQL(SQL).format(sql.Identifier(TABLE_NAMES['vehicles']), sql.Identifier(TABLE_NAMES['datapoints']), sql.Identifier(TABLE_NAMES['datapoints']))
                data = (i['id'],)
                cur.execute(SQL, data)
                vehicles = cur.fetchall()
                if vehicles == None:
                    print("There are no results for vehicles query")
                    vehicles = []
                
                v_columns = [desc[0] for desc in cur.description]
                for v in vehicles:
                    v = dict(zip(v_columns, v))
                    v['tags'] = []
                    print(json.dumps(v))
                    
                    SQL = "SELECT epc FROM {} where vehicle_id = %s order by epc;" 
                    SQL = sql.SQL(SQL).format(sql.Identifier(TABLE_NAMES['tags']))
                    data = (v['id'],)
                    cur.execute(SQL, data)
                    tags = cur.fetchall()
                    if tags == None:
                        print("There are no tags for this vehicles")
                        tags = []
                    
                    t_columns = [desc[0] for desc in cur.description]
                    for t in tags:
                        t = dict(zip(t_columns, t))
                        print(json.dumps(t))
                        v['tags'].append(t)
                    
                    i['vehicles'].append(v)


        conn.commit()
        cur.close()
        return jsonify(result)

    def post(self):
        content = request.json
        print(content)
        
        username = content.get('username', None)
        email = content.get('email', None)
        name = content.get('name', None)
        given_name  = content.get('given_name', None)
        family_name  = content.get('family_name', None)
        preferred_username  = content.get('preferred_username', None)
        cognito_user_status  = content.get('cognito:user_status', True)
        status = content.get('status', 0)
        sub  = content.get('sub', None)
        
        conn = get_db()
        cur = conn.cursor()
        
        SQL = "INSERT INTO {} (username, email, name, given_name, family_name, preferred_username, \"cognito:user_status\", status, sub) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;" 
        SQL = sql.SQL(SQL).format(sql.Identifier(TABLE_NAMES['users']))
        data = (username, email, name, given_name, family_name, preferred_username, cognito_user_status, status, sub)
        cur.execute(SQL, data) 
        id_of_new_row = cur.fetchone()[0]        
        
        conn.commit()
        cur.close()
        
        return id_of_new_row, 201

# User
# shows a single User item and lets you delete a User item
class User(Resource):
    def get(self, user_id):
        
        try:
            int(user_id)
        except ValueError: 
            return None # the input is not an integer
        
        conn = get_db()
        cur = conn.cursor()
        SQL = "SELECT * FROM {} where id = %s limit 1;" 
        SQL = sql.SQL(SQL).format(sql.Identifier(TABLE_NAMES['users']))
        data = (user_id,) # keep the comma to make it a tuple
        cur.execute(SQL, data) 
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

    def delete(self, user_id):
        conn = get_db()
        cur = conn.cursor()
        
        SQL = "DELETE FROM {} WHERE id = %s;" 
        SQL = sql.SQL(SQL).format(sql.Identifier(TABLE_NAMES['users']))
        data = (user_id, )
        cur.execute(SQL, data) 
        
        conn.commit()
        cur.close()
        return '', 204

    def post(self, user_id):
        content = request.json #: :type content: dict
        print(content)
        
        if content is None: return None, 304
        
        username = content.get('username', None)
        email = content.get('email', None)
        name = content.get('name', None)
        given_name  = content.get('given_name', None)
        family_name  = content.get('family_name', None)
        preferred_username  = content.get('preferred_username', None)
        cognito_user_status  = content.get('cognito:user_status', True)
        status = content.get('status', 0)
        sub  = content.get('sub', None)        
        
        conn = get_db()
        cur = conn.cursor()
        
        inputslist = []
        SQL = "UPDATE {} SET lastupdate = now()" 
        if 'username' in content :
            SQL += ', username = %s'
            inputslist.append(username)
        if 'email' in content :
            SQL += ', email = %s'
            inputslist.append(email)
        if 'name' in content :
            SQL += ', name = %s'
            inputslist.append(name)
        if 'given_name' in content :
            SQL += ', given_name = %s'
            inputslist.append(given_name)
        if 'family_name' in content :
            SQL += ', family_name = %s'
            inputslist.append(family_name)
        if 'preferred_username' in content :
            SQL += ', preferred_username = %s'
            inputslist.append(preferred_username)
        if 'cognito:user_status' in content :
            SQL += ', \"cognito:user_status\" = %s'
            inputslist.append(cognito_user_status)
        if 'status' in content :
            SQL += ', status = %s'
            inputslist.append(status)
        if 'sub' in content :
            SQL += ', sub = %s'
            inputslist.append(sub)
        
        SQL += " where id = %s RETURNING id;"
        SQL = sql.SQL(SQL).format(sql.Identifier(TABLE_NAMES['users']))
        inputslist.append(user_id)
        
        data = tuple(inputslist)
        cur.execute(SQL, data) 
        id_of_new_row = cur.fetchone()[0]        
        
        conn.commit()
        cur.close()
        
        return id_of_new_row, 201
