from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_PORT"] = 3307
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "Nirvana813"
app.config["MYSQL_DB"] = "todos"

mysql = MySQL(app)


# Initialize the database schema
def initialize_database():
    with app.app_context():
        cur = mysql.connection.cursor()

        # Drop todos table if it exists
        cur.execute("DROP TABLE IF EXISTS todos")

        # Create todos table
        cur.execute("""
            CREATE TABLE todos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                due_date DATE
            );
        """)

        # Insert initial data
        initial_data = [
            ('buy avocado', 'dont forget to buy a avocado', '2024-02-23'),
            ('walk a dog', 'dont forget to walk a dog', '2024-07-28'),
            ('learn coding', 'learn python', '2024-09-10'),
            ('buy new shoes', 'i dont have enough shoes', '2024-10-21')
        ]

        cur.executemany("""
            INSERT INTO todos (title, description, due_date) 
            VALUES (%s, %s, %s)
        """, initial_data)

        mysql.connection.commit()
        cur.close()


# Call the initialize_database function
initialize_database()



# ENDPOINT, paths to resource, URL
@app.route('/')
def hello_world():  # put application's code here
    return f'Hello, World!'


# Endpoint
@app.route('/todos')
def show_todos():
    # Retrieve todos from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM todos")
    todos_from_db = cur.fetchall()
    cur.close()

    # Return HTML page through render template with passing variables
    return render_template("index.html", todos=todos_from_db, name="Lucia")


@app.route('/create', methods=["POST"])
def create():
    # Retrieve data from FORM from HTML (attribute name)
    title = request.form['title']
    description = request.form['description']
    due_date = request.form['date']

    cur = mysql.connection.cursor()

    cur.execute("INSERT INTO todos (title, description, due_date) VALUES (%s, %s, %s)", (title, description, due_date))

    mysql.connection.commit()
    cur.close()

    # Redirect to another endpoint, function with name show_todos
    return redirect(url_for("show_todos"))


# ROUTE PARAMETERS, PATH VARIABLE in <>
@app.route('/delete/<todo_id>')
def delete(todo_id):
    cur = mysql.connection.cursor()

    # Delete todo from the database
    cur.execute("DELETE FROM todos WHERE id = %s", (todo_id,))

    mysql.connection.commit()
    cur.close()

    return redirect(url_for("show_todos"))


@app.route('/update/<todo_id>', methods=["POST", "GET"])
def update(todo_id):
    # If request method is GET, then render update HTML page
    if request.method == "GET":
        cur = mysql.connection.cursor()

        # Retrieve todo from the database
        cur.execute("SELECT * FROM todos WHERE id = %s", (todo_id,))
        todo_from_db = cur.fetchone()
        cur.close()

        return render_template("update.html", todo=todo_from_db)

    # If request method is POST (from FORM in update HTML) then you retrieve data from form and redirect to show_todos
    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        due_date = request.form['date']

        cur = mysql.connection.cursor()

        # Update todo in the database
        cur.execute("UPDATE todos SET title=%s, description=%s, due_date=%s WHERE id=%s",
                    (title, description, due_date, todo_id))

        mysql.connection.commit()
        cur.close()

        return redirect(url_for("show_todos"))


if __name__ == '__main__':
    app.run()
