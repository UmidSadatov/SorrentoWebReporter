from flask import Flask, render_template, request, redirect, url_for, session, render_template_string
import os
from werkzeug.utils import secure_filename
from reporter import *
from jsoner import *
from db_manage import *

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
    session['secondary_file_input_groups'] = [
        {
            "dist": "",
            "name_cells_template": "",
            "region1_cells_template": "",
            "region2_cells_template": "",
            "sales_cells_template": "",            
            "client_cells_template": "",
            "sheet_index": "0",
            "input_error": False
        }
    ]
    
    session['secondary_staff_input_groups'] = json_to_var('static/staffs.json')
    for staff_data in session['secondary_staff_input_groups']:
        staff_data['saved'] = True

    session['error'] = ""
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
        regions=regions,
        error="",
    )


@app.route('/secondary_processing', methods=['POST'])
def secondary_processing():
    # files
    distributors = request.form.getlist('distributor')
    name_templates = request.form.getlist('name_template')
    region1_templates = request.form.getlist('region1_template')
    region2_templates = request.form.getlist('region2_template')
    sales_templates = request.form.getlist('sales_template')
    client_templates = request.form.getlist('client_template')
    files = request.files.getlist('file')
    pages = request.form.getlist('sheet_index')

    # Удаление старых файлов
    for old_file in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], old_file)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)  # Удаление файла или ссылки

    # Сохранение новых файлов
    for file in files:
        if file.filename != '':
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

    session['secondary_file_input_groups'] = []
    file_report_dicts = []
    input_errors_count = 0

    for i in range(0, len(distributors)):
        session['secondary_file_input_groups'].append(
            {
                "dist": distributors[i],
                "name_cells_template": name_templates[i],
                "region1_cells_template": region1_templates[i],
                "region2_cells_template": region2_templates[i] if region2_templates[i] is not None else "",
                "sales_cells_template": sales_templates[i],            
                "client_cells_template": client_templates[i] if client_templates[i] is not None else "",
                "sheet_index": pages[i],
                "input_error": False
            }
        )

        try:
            new_report_dict = get_report_dict_from_file(
                filename=f"uploads/{files[i].filename}",
                dist=str(distributors[i]),
                name_cells_template=str(name_templates[i]),
                region1_cells_template=region1_templates[i],
                region2_cells_template=region2_templates[i] if region2_templates[i] != "" else None,
                sales_cells_template=sales_templates[i],
                client_cells_template=client_templates[i] if client_templates[i] != "" else None,
                sheet_index=int(pages[i])
            )
            file_report_dicts.append(new_report_dict)
        except Exception as error:
            print(error)
            session['secondary_file_input_groups'][-1]["input_error"] = True
            input_errors_count += 1


    #staffs
    staff_names = request.form.getlist('staff')
    groups = request.form.getlist('group')
    checkboxes = request.form.getlist('save_checkbox')
    regions = []
    session['secondary_staff_input_groups'] = []
    saved_staffs_data = []

    for i in range(0, len(staff_names)):
        regions_list = request.form.getlist(f'fg{i+1}_regions')
        regions.append(regions_list)

        session['secondary_staff_input_groups'].append(
            {
                'staff': staff_names[i],
                'group': groups[i],
                'regions': regions_list,
                'saved': f'save_checkbox_{i+1}' in checkboxes
            }
        )

        if f'save_checkbox_{i+1}' in checkboxes:
            saved_staffs_data.append(
                {
                    'staff': staff_names[i],
                    'group': groups[i],
                    'regions': regions_list,
                }
            )
        
        var_to_json(saved_staffs_data, "static/staffs.json")

        # print(staff_names[i])
        # print(groups[i])
        # print(regions_list)
        # print(f"saved: {f'save_checkbox_{i+1}' in checkboxes}")
        # print('\n\n')

    if input_errors_count > 0:
        session['error'] = "Ошибка ввода"
        return redirect(url_for('secondary'))
    
    total_report_dict = get_total_report_dict(*file_report_dicts)
    session['not_found_names'] = total_report_dict['not_found_names']
    session['not_found_regions'] = total_report_dict['not_found_regions']

    general_regions = get_general_regions()
    
    return render_template(
        'secondary_data_normalization.html',
        general_regions=general_regions
        )


@app.route('/downloadsecondaryreport', methods=['POST'])
def send_file():

    for i in range(0, len(session['not_found_regions'])):
        try:
            unique = session['not_found_regions'][i]
            general = request.form[f'general_region_select{i}']

            insert_region(unique, general)
            print('\n' , unique, '  :  ', general)

        except KeyError:
            pass


    # general_region_selects = request.form.getlist('general_region_select')

    # print(session['not_found_regions'])
    # print(general_region_selects)

    # for i in range(0, len(session['not_found_regions'])):
    #     if general_region_selects[i] is not None and len(general_region_selects[i]):
    #         unique = session['not_found_regions'][i]
    #         general = general_region_selects[i]
    #         # insert_region(unique, general)
    #         print(unique, '  :  ', general)
    
    return "<h1>Генерация файла</h1>"
    
    
























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
