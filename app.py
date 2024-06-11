from flask import Flask, render_template, request, redirect, url_for, session, render_template_string
import os
from werkzeug.utils import secure_filename
from reporter import *
from jsoner import *

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Настройка директории для загрузки файлов
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
def auth():
    auth_error = False

    if request.method == 'POST':
        user = request.form.get('user')
        password = request.form.get('password')

        users = json_to_var("static/users.json")
        found = False
        
        for account in users:
            if account['user'] == user and account['password'] == password:
                found = True
                break
        
        if found:
            return redirect('/home')
        else:
            auth_error = True
    
    return render_template('auth.html', auth_error=auth_error)


@app.route('/home')
def home():
    session['secondary_files_data'] = [
        {
            "dist": "Pharm Luxe",
            "name_cells_template": "",
            "region1_cells_template": "",
            "sales_cells_template": "",
            "region2_cells_template": "",
            "client_cells_template": "",
            "sheet_index": "0"
        }
    ]
    return render_template('home.html')


@app.route('/primary')
def primary():
    pass


@app.route('/secondary')
def secondary():
    distributors = [
        "Pharm Luxe",
        "Grand Pharm",
        "Meros Pharm",
        "Whole Pharm",
        "Young Pharm",
        "Akmal Pharm",
        "OxyMed",
        "Grand apteka",
        "Best Pharm",
        "Zenta Pharm",
        "Pharma Choice",
        "Pharma Cosmos",
        "Navbahor",
        "Tabletka"
    ]

    groups = [
        "C&P",
        "OTC",
        "RX",
        "Eco",
        "Gastro"
    ]

    regions = [
        'Алмазарский р. (Ташкент)',
        'Бектемирский р. (Ташкент)',
        'Мирабадский р. (Ташкент)',
        'М.Улугбекский р. (Ташкент)',
        'Сергелийский р. (Ташкент)',
        'Чиланзарский р. (Ташкент)',
        'Шайхантахурский р. (Ташкент)',
        'Юнусабадский р. (Ташкент)',
        'Яккасарайский р. (Ташкент)',
        'Яшнабадский р. (Ташкент)',
        'Учтепинский р. (Ташкент)',
        'Ташкентская обл.',
        'Андижанская обл.',
        'Наманганская обл.',
        'Ферганская обл.',
        'Сырдарьинская обл.',
        'Джизакская обл.',
        'Самаркандская обл.',
        'Кашкадарьинская обл.',
        'Сурхандарьинская обл.',
        'Бухарская обл.',
        'Навоинская обл.',
        'Хорезмская обл.',
        'Респ. Каракалпакстан'
    ]

    return render_template(
        'secondary.html', 
        distributors=distributors, 
        groups=groups,
        regions=regions
    )




@app.route('/home_old')
def home_old():
    session['secondary_file_datas'] = [
        {
            "dist": "Pharm Luxe",
            "name_cells_template": "",
            "region1_cells_template": "",
            "sales_cells_template": "",
            "region2_cells_template": "",
            "client_cells_template": "",
            "sheet_index": "0"
        }
    ]
    return render_template('index.html')

@app.route('/primary_old')
def primary_old():
    return render_template('primary.html')

@app.route('/secondary_old', methods=['GET', 'POST'])
def secondary_old():
    distributors = [
        "Pharm Luxe",
        "Grand Pharm",
        "Meros Pharm",
        "Whole Pharm",
        "Young Pharm",
        "Akmal Pharm",
        "OxyMed",
        "Grand apteka",
        "Best Pharm",
        "Zenta Pharm",
        "Pharma Choice",
        "Pharma Cosmos",
        "Navbahor",
        "Tabletka"
    ]

    return render_template('secondary.html', distributors=distributors)

@app.route('/process_files', methods=['POST'])
def process_files():

    distributors = request.form.getlist('distributor')
    name_templates = request.form.getlist('name_template')
    region1_templates = request.form.getlist('region1_template')
    region2_templates = request.form.getlist('region2_template')
    sales_templates = request.form.getlist('sales_template')
    client_templates = request.form.getlist('client_template')
    files = request.files.getlist('file')
    pages = request.form.getlist('sheet_index')

    session['secondary_file_datas'] = []

    # Сохранение файлов
    for file in files:
        if file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    files_report_dicts = []
    
    for i in range(0, len(distributors)):

        dist = distributors[i]
        name_cells_template = name_templates[i]
        region1_cells_template = region1_templates[i]
        sales_cells_template = sales_templates[i]
        sheet_index = pages[i]

        if len(region2_templates[i]):
            region2_cells_template = region2_templates[i]
        else:
            region2_cells_template = None

        if len(client_templates[i]):
            client_cells_template = client_templates[i]
        else:
            client_cells_template = None



        session['secondary_file_datas'].append(
            {
                "dist": dist,
                "name_cells_template": name_cells_template,
                "region1_cells_template": region1_cells_template,
                "sales_cells_template": sales_cells_template,
                "region2_cells_template": region2_cells_template if region2_cells_template is not None else "",
                "client_cells_template": client_cells_template if client_cells_template is not None else "",
                "file": files[i].filename,
                "sheet_index": str(sheet_index)
            }
        )


        files_report_dicts.append(
            get_report_dict_from_file(
                filename=f"uploads/{files[i].filename}",
                dist=dist,
                name_cells_template=name_cells_template,
                region1_cells_template=region1_cells_template,
                sales_cells_template=sales_cells_template,
                region2_cells_template=region2_cells_template,
                client_cells_template=client_cells_template,
                sheet_index=int(sheet_index)
            )
        )

    total_report_dict = get_total_report_dict(*files_report_dicts)

        
    return render_template_string(
        "{% for n in nfn %}"
        "<p>{{n}}</p>"
        "{% endfor %}",
        nfn=total_report_dict['not_found_names']
    )

    # return redirect(url_for('secondary'), code=307)

if __name__ == '__main__':
    app.run(debug=True)
