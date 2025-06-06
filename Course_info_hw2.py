from flask import Flask
from flask import render_template_string
from flask import request
from flask import jsonify
import pandas as pd
import os

app = Flask(__name__)
app.debug = True

def load_data():
    files = {
        'big-hw-01': 'Python_big_hw_01.csv',
        'hw-02': 'Python_hw_02.csv'
    }

    dfs = []
    for hw_alias, filename in files.items():
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename, header=None, names=['student_name_raw', 'group_id', 'mr_link', 'score_raw', 'comment1', 'comment2', 'deadline'])

                if df.iloc[0]['group_id'] == 'Группа':
                    df = df.iloc[1:].copy()

                df['hw_name'] = hw_alias
                dfs.append(df)
            except Exception as e:
                print(f"Error while uploading a file {filename}: {e}")
        else:
            print(f"file {filename} is not found.")

    if not dfs:
        print("Could not load any DataFrame.")
        return pd.DataFrame()

    combined_df = pd.concat(dfs, ignore_index=True)

    combined_df['student_name'] = combined_df['student_name_raw'].str.strip()
    combined_df.drop(columns=['student_name_raw'], inplace=True)

    combined_df['group_id'] = pd.to_numeric(combined_df['group_id'], errors='coerce').fillna(0).astype(int)

    combined_df['score'] = pd.to_numeric(combined_df['score_raw'], errors='coerce').fillna(0)
    combined_df.drop(columns=['score_raw'], inplace=True)

    return combined_df

df = load_data()


if df.empty:
    print("warning: application is running without data")

def compute_mark(score):
    if pd.isna(score) or score <= 0:
        return 2
    elif score >= 50:
        return 5
    elif score >= 30:
        return 4
    elif score >= 1:
        return 3
    else: # На всякий случай, если score отрицательный или иное
        return 2


@app.route('/')
def index():
    return "A service for obtaining information about the course. Available endpoints: /names, /&lt;hw-name&gt;/mean_score, /&lt;hw-name&gt;/&lt;group-id&gt;/mean_score, /mean_score, /mark, /course_table"

@app.route('/names')
def names():
    if df.empty:
        return jsonify({'status': 'error', 'message': 'The data has not been uploaded.'}), 500
    unique_names = df['student_name'].dropna().unique().tolist()
    return jsonify({'names': sorted(unique_names)})

@app.route('/<hw_name>/mean_score')
def hw_mean_score(hw_name):
    if df.empty:
        return jsonify({'status': 'error', 'message': 'The data has not been uploaded.'}), 500
    if hw_name not in df['hw_name'].unique():
        return jsonify({'status': 'error', 'message': f'hw "{hw_name}" is not found.'}), 404

    mean_score = df[df['hw_name'] == hw_name]['score'].mean()
    return jsonify({'hw_name': hw_name, 'mean_score': round(mean_score, 2) if pd.notna(mean_score) else None})

@app.route('/<hw_name>/<int:group_id>/mean_score')
def hw_group_mean_score(hw_name, group_id):
    if df.empty:
        return jsonify({'status': 'error', 'message': 'The data has not been uploaded.'}), 500
    filtered = df[(df['hw_name'] == hw_name) & (df['group_id'] == group_id)]
    if filtered.empty:
        return jsonify({'status': 'error', 'message': f'Data for hw "{hw_name}" and group "{group_id}" are not found.'}), 404

    mean_score = filtered['score'].mean()
    return jsonify({'hw_name': hw_name, 'group_id': group_id, 'mean_score': round(mean_score, 2) if pd.notna(mean_score) else None})

@app.route('/mean_score')
def mean_score_query():
    hw_name = request.args.get('hw_name')
    group_id_str = request.args.get('group_id')

    if not hw_name or not group_id_str:
        return jsonify({'status': 'error', 'message': 'Required parameters are missing: group_id и hw_name.'}), 400

    try:
        group_id = int(group_id_str)
    except ValueError:
        return jsonify({'status': 'error', 'message': 'The group_id parameter must be a number..'}), 400


    return hw_group_mean_score(hw_name, group_id)

@app.route('/mark')
def mark():
    if df.empty:
        return jsonify({'status': 'error', 'message': 'The data has not been uploaded.'}), 500

    student_id = request.args.get('student_id')
    group_id_str = request.args.get('group_id')

    if not student_id and not group_id_str:
        return jsonify({'status': 'error', 'message': 'You must specify either student_id or group_id.'}), 400

    if student_id:
        student_data = df[df['student_name'].str.contains(student_id.strip(), case=False, na=False)]

        if student_data.empty:
            return jsonify({'status': 'error', 'message': f'Student "{student_id}" is not found.'}), 404

        total_score = student_data['score'].sum()
        mark = compute_mark(total_score)
        return jsonify({'student_id': student_id, 'total_score': float(total_score), 'mark': mark})

    elif group_id_str:
        try:
            group_id = int(group_id_str)
        except ValueError:
            return jsonify({'status': 'error', 'message': 'The group_id parameter must be a number..'}), 400

        group_data = df[df['group_id'] == group_id]

        if group_data.empty:
            return jsonify({'status': 'error', 'message': f'Group "{group_id}" is not found.'}), 404

        average_group_score = group_data['score'].mean()
        mean_mark = compute_mark(average_group_score)
        return jsonify({'group_id': group_id, 'average_score': float(average_group_score), 'mean_mark': mean_mark})

@app.route('/course_table')
def course_table():
    if df.empty:
        return jsonify({'status': 'error', 'message': 'The data has not been uploaded.'}), 500

    hw_name = request.args.get('hw_name')
    group_id_str = request.args.get('group_id')

    filtered_df = df.copy()
    title = "Table of students"

    if hw_name and group_id_str:
        try:
            group_id = int(group_id_str)
        except ValueError:
            return jsonify({'status': 'error', 'message': 'The group_id parameter must be a number..'}), 400

        if hw_name not in df['hw_name'].unique():
            return jsonify({'status': 'error', 'message': f'hw "{hw_name}" is not found.'}), 404

        filtered_df = filtered_df[(filtered_df['hw_name'] == hw_name) & (filtered_df['group_id'] == group_id)]
        title = f"Homework table '{hw_name}' and group '{group_id}'"
    elif hw_name:
        if hw_name not in df['hw_name'].unique():
            return jsonify({'status': 'error', 'message': f'hw "{hw_name}" is not found.'}), 404
        filtered_df = filtered_df[filtered_df['hw_name'] == hw_name]
        title = f"Homework table '{hw_name}' (all groups)"
    elif group_id_str:
        try:
            group_id = int(group_id_str)
        except ValueError:
            return jsonify({'status': 'error', 'message': 'The group_id parameter must be a number..'}), 400
        filtered_df = filtered_df[filtered_df['group_id'] == group_id]
        title = f"Homework table '{group_id}' (all hw)"
    else:
        return jsonify({'status': 'error', 'message': 'You must specify the hw_name or group_id for rendering the table..'}), 400

    if filtered_df.empty:
        return jsonify({'status': 'error', 'message': 'No data was found for the specified parameters.'}), 404

    result_df = filtered_df[['student_name', 'group_id', 'score']].copy()
    result_df['mark'] = result_df['score'].apply(compute_mark)
    result_df.sort_values(['group_id', 'student_name'], inplace=True)

    students_data = result_df.to_dict('records')

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{{ title }}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>{{ title }}</h1>

        {% if students %}
        <table>
            <thead>
                <tr>
                    <th>Имя Студента</th>
                    <th>Группа</th>
                    <th>Баллы</th>
                    <th>Оценка</th>
                </tr>
            </thead>
            <tbody>
                {% for student in students %}
                <tr>
                    <td>{{ student.student_name }}</td>
                    <td>{{ student.group_id }}</td>
                    <td>{{ student.score }}</td>
                    <td>{{ student.mark }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p>Нет данных для отображения.</p>
        {% endif %}

    </body>
    </html>
    """
    return render_template_string(html_template,
                                  students=students_data,
                                  title=title)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1337)