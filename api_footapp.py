import mysql.connector
from flask import Flask, jsonify, request

# Configurações de conexão
config = {
    'user': 'root',
    'password': 'vinicius15',
    'host': '127.0.0.1',
    'database': 'db_footapp'
}

def close_db_connection(conn, cursor):
    cursor.close()
    conn.close()

class Game:
    def __init__(self, id, team1, team2, score1, score2, championship, date, country2, country1, type, rate):
        self.id = id
        self.team1 = team1
        self.team2 = team2
        self.score1 = score1
        self.score2 = score2
        self.championship = championship
        self.country1 = country1
        self.country2 = country2
        self.type = type
        self.date = str(date)
        self.rate = rate

class comentario:
    def __init__(self,userid,username,comentario,image):
        self.userid = userid
        self.name = username
        self.comment = comentario
        self.image = image

class comentario_user:
    def __init__(self, id, team1, team2, score1, score2, championship, date, country2, country1, type,comment):
        self.id = id
        self.team1 = team1
        self.team2 = team2
        self.score1 = score1
        self.score2 = score2
        self.championship = championship
        self.country1 = country1
        self.country2 = country2
        self.type = type
        self.date = str(date)
        self.comment = comment

class review_user:
    def __init__(self, id, team1, team2, score1, score2, championship, date, country2, country1, type,nota):
        self.id = id
        self.team1 = team1
        self.team2 = team2
        self.score1 = score1
        self.score2 = score2
        self.championship = championship
        self.country1 = country1
        self.country2 = country2
        self.type = type
        self.date = str(date)
        self.nota = nota

app = Flask(__name__)

@app.route("/games/rise", methods=["GET"])
def search_games_rise():

    # Estabelecendo a conexão
    conn = mysql.connector.connect(**config)
    # Criando cursor
    cursor = conn.cursor()

    try:
        if conn:
            games = []
            cursor.execute("SELECT g.*, COALESCE(AVG(r.nota), 0) AS media_avaliacao FROM games g INNER JOIN reviews r ON r.gameid = g.id GROUP BY g.id ORDER BY media_avaliacao DESC limit 10;")
            resultados = cursor.fetchall()
            cursor.close()
            for linha in resultados:
                games.append(Game(*linha))
            return jsonify([game.__dict__ for game in games])
        else:
            return jsonify({"error": "Failed to connect to database"}), 500
    except Exception as e:
        return jsonify({"error": f'{e}'}), 500
    finally:
        close_db_connection(conn, cursor)

@app.route("/games/today", methods=["GET"])
def search_games_today():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    try:
        if conn:
            cursor = conn.cursor()
            games = []
            cursor.execute(f"select g.*, coalesce(avg(r.nota),0) from games g left join reviews r on r.gameid = g.id where gamedate > curdate() and gamedate < curdate() + INTERVAL 1 DAY group by g.id;")
            resultados = cursor.fetchall()
            for linha in resultados:
                games.append(Game(*linha))
            cursor.close()
            return jsonify([game.__dict__ for game in games])
        else:
            return jsonify({"error": "Failed to connect to database"}), 500
    except Exception as e:
        return jsonify({"error": 'aqui'}), 500
    finally:
        close_db_connection(conn, cursor)

@app.route("/games/now", methods=["GET"])
def search_games_now():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    try:
        if conn:
            cursor = conn.cursor()
            games = []
            cursor.execute(f"select g.*, coalesce(avg(r.nota),0) from games g left join reviews r on r.gameid = g.id where gamedate < now() and gamedate > date_sub(now(), interval 2 hour) group by g.id")
            resultados = cursor.fetchall()
            for linha in resultados:
                games.append(Game(*linha))
            cursor.close()
            return jsonify([game.__dict__ for game in games])
        else:
            return jsonify({"error": "Failed to connect to database"}), 500
    except Exception as e:
        return jsonify({"error": e}), 500
    finally:
        close_db_connection(conn, cursor)

@app.route("/games/review", methods=["POST"])
def post_review():

    req = request.get_json()
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    try:
        gameid = req['gameid']
        userid = req['userid']
        grade = req['grade']
        if conn:
            cursor.execute("INSERT INTO reviews (userid, nota, gameid) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE nota = VALUES(nota);", (userid, grade, gameid))
            conn.commit()
            return jsonify({'gameid':gameid,'userid':userid,'grade':grade})
        else:
            return jsonify({"error": "Failed to connect to database"}), 500
    except mysql.connector.Error as e:
        return jsonify(),400
    except Exception as e:
        return jsonify({"error": e}), 500
    finally:
        close_db_connection(conn, cursor)

@app.route("/games/review/<gameid>/<userid>", methods=["GET"])
def get_review(gameid,userid):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    try:
        if conn:
            cursor.execute("select nota from reviews where gameid=%s and userid=%s", (gameid, userid))
            resultados = cursor.fetchone()
            if resultados == None:
                return jsonify(),400
            return jsonify({'grade':resultados[0]})
        else:
            return jsonify({"error": "Failed to connect to database"}), 500
    except Exception as e:
        return jsonify({"error": e}), 500
    finally:
        close_db_connection(conn, cursor)

@app.route("/games/comments", methods=["POST"])
def post_comment():
    req = request.get_json()
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    try:
        gameid = req['gameid']
        userid = req['userid']
        comment = req['comment']
        if conn:
            cursor.execute("insert into comments values(%s,%s,%s)", (gameid, userid, comment))
            conn.commit()
            return jsonify({'gameid':gameid,'userid':userid,'comment':comment})
        else:
            return jsonify({"error": "Failed to connect to database"}), 500
    except mysql.connector.Error as e:
        return jsonify(),400
    except Exception as e:
        return jsonify({"error": e}), 500
    finally:
        close_db_connection(conn, cursor)

@app.route("/teams/<team>",methods=["GET"])
def get_team(team):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    if conn:
            cursor.execute("select url_image, color from teams where name = %s;",(team,))
            resultados = cursor.fetchone()
            if(resultados == None):
                return jsonify(),400
            return jsonify({'url_image':resultados[0],'color':resultados[1]})
    else:
            return jsonify({"error": "Failed to connect to database"}), 500

@app.route("/games/comments/<id>/<page>", methods=["GET"])
def get_comments(id,page):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    try:
        if conn:
            cursor.execute("select u.id,u.name, c.comment, u.url_image from comments c inner join users u on c.userid = u.id where gameid = %s limit 10 offset %s", (id,int(page),))
            resultados = cursor.fetchall()
            comentarios = []
            for linha in resultados:
                comentarios.append(comentario(*linha))
            return jsonify([comentario.__dict__ for comentario in comentarios])
        else:
            return jsonify({"error": "Failed to connect to database"}), 500
    except Exception as e:
        return jsonify({"error": e}), 500
    finally:
        close_db_connection(conn, cursor)

@app.route("/users/<id>", methods=["GET"])
def user_profile(id):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    try:
        if conn:
            cursor.execute("SELECT u.name, u.url_image, (select count(nota) from reviews where userid = u.id) AS qtd_nota, COUNT(DISTINCT c.comment)"+
                           " AS qtd_comentarios FROM users u left JOIN reviews r ON u.id = r.userid "+
                           "left JOIN comments c ON u.id = c.userid WHERE u.id = %s", (id,))
            resultados = cursor.fetchone()
            if(resultados[0] == None):
                return jsonify(), 400
            return jsonify({'username':resultados[0],'image':resultados[1],'qtd_notas':resultados[2],'qtd_comentarios':resultados[3]})
        else:
            return jsonify({"error": "Failed to connect to database"}), 500
    except Exception as e:
        return jsonify({"error": e}), 500
    finally:
        close_db_connection(conn, cursor)

@app.route("/users/login", methods=["POST"])
def login():
    req = request.get_json()
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    try:
        name = req['username']
        email = req['email']
        userid = req['userid']
        image = req['image']
        if conn:
            cursor.execute("insert into users (name,email,url_image) values (%s,%s,%s) as new_user on duplicate key update name = new_user.name,url_image=new_user.url_image", (name,email,image,))
            conn.commit()
            cursor.execute("select * from users where email = %s",(email,))
            resultados = cursor.fetchall()
            for linha in resultados:
                userid = linha[0]
                name = linha[1]
                email = linha[2]
                image = linha[3]
            return jsonify({'userid':userid,'username':name,'email':email,'image':image})
        else:
            return jsonify({"error": "Failed to connect to database"}), 500
    except Exception as e:
        return jsonify({"error": e}), 500
    finally:
        close_db_connection(conn, cursor)

@app.route("/users/comment/<id>/<offset>", methods=["GET"])
def get_user_comments(id,offset):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    try:
        if conn:
            cursor.execute("select g.*,comment from comments c inner join games g on c.gameid = g.id where c.userid = %s limit 10 offset %s", (id,int(offset)))
            resultados = cursor.fetchall()
            lista = []
            cursor.close()
            for linha in resultados:
                lista.append(comentario_user(*linha))
            return jsonify([comentario_user.__dict__ for comentario_user in lista])
        else:
            return jsonify({"error": "Failed to connect to database"}), 500
    except Exception as e:
        return jsonify({"error": e}), 500
    finally:
        close_db_connection(conn, cursor)

@app.route("/users/review/<id>/<offset>", methods=["GET"])
def get_user_review(id,offset):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    try:
        if conn:
            cursor.execute("select g.*,nota from reviews r inner join games g on r.gameid = g.id where r.userid = %s limit 10 offset %s", (id,int(offset)))
            resultados = cursor.fetchall()
            lista = []
            cursor.close()
            for linha in resultados:
                lista.append(review_user(*linha))
            return jsonify([review_user.__dict__ for review_user in lista])
        else:
            return jsonify({"error": "Failed to connect to database"}), 500
    except Exception as e:
        return jsonify({"error": e}), 500
    finally:
        close_db_connection(conn, cursor)

if __name__ == "__main__":
    app.run(port=5000, host='localhost', debug=True)
