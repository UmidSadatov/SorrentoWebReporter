from excel_processing import ExcelBook
from db_manage import get_all_names, get_general_name, get_general_region, check_name
from divisions import *
from expander import expand




def get_report_dict_from_file(
        filename:str,
        dist:str,
        name_cells_template: str,
        region1_cells_template: str,
        sales_cells_template: str,
        region2_cells_template: str | None = None,
        client_cells_template: str | None = None,
        sheet_index=0
    ):
    """
        {
            "distributor": ...,
            "data": {
                "group1": {
                
                    "name1": {
                        "Total": 0,
                        "reg1": 0,
                        "reg2": 0,
                        ...,
                        "Неизвестный р.": 0 
                    },

                    "name2": {
                        "Total": 0,
                        "reg1": 0,
                        "reg2": 0,
                        ...,
                        "Неизвестный р.": 0 
                    },
                    ...

                }
                
            },
            "not_found_names": [],
            "not_found_regions": []
        }
    """
    data = get_all_names()
    not_found_names = []
    not_found_regions = []
    xl_file = ExcelBook(filename)
    max_row = str(int(xl_file.get_max_row(sheet_index=sheet_index)))

    name_cells = expand(name_cells_template.replace("#", max_row))
    region1_cells = expand(region1_cells_template.replace("#", max_row))
    sales_cells = expand(sales_cells_template.replace("#", max_row))

    region2_cells = expand(region2_cells_template.replace("#", max_row)) \
        if region2_cells_template is not None else None
    
    client_cells = expand(client_cells_template.replace("#", max_row)) \
        if client_cells_template is not None else None
    

    for i in range(0, len(name_cells)):
        name_cell = name_cells[i]
        region1_cell = region1_cells[i]
        sales_cell = sales_cells[i]
        region2_cell = None
        client_cell = None

        if region2_cells is not None:
            region2_cell = region2_cells[i]

        if client_cells is not None:
            client_cell = client_cells[i]
        
        #####################################################
        name_in_cell = str(xl_file.get_cell_value(name_cell, sheet_index=sheet_index))
        name = get_general_name(name_in_cell)

        if name is not None:
            region1 = xl_file.get_cell_value(region1_cell, sheet_index=sheet_index)

            region2 = ""
            if region2_cell is not None:
                region2 = xl_file.get_cell_value(region2_cell, sheet_index=sheet_index)
            
            region = "Неизвестный р."
            genreg1 = get_general_region(region1)
            genreg2 = get_general_region(region2)
            genreg3 = get_general_region(f"{region1} {region2}")
            if genreg1 is not None:
                region = genreg1
            elif genreg2 is not None:
                region = genreg2
            elif genreg3 is not None:
                region = genreg3
                
            
            sales = int(abs(xl_file.get_cell_value(sales_cell, sheet_index=sheet_index)))

            client = xl_file.get_cell_value(client_cell, sheet_index=sheet_index) if client_cell is not None else None

            for group in data:
                if name in data[group]:                    
                    if client in non_division_buyers:
                            continue
                    elif client in divided_clients_list:
                        data[group][name]['Total'] += sales
                        for clients_tuple in divided_sellings:
                            if client in clients_tuple:
                                regions_indices = divided_sellings[clients_tuple]
                                regions_name_list = get_regions(regions_indices)
                                chunk_sales = round(sales / len(regions_indices))
                                rest_of_sales = sales - chunk_sales * len(regions_indices)
                                data[group][name]["Неизвестный р."] += rest_of_sales
                                for reg in regions_name_list:
                                    data[group][name][reg] += chunk_sales
                                break
                    else:
                        data[group][name]['Total'] += sales
                        data[group][name][region] += sales
                        if region == 'Неизвестный р.':
                            not_found_regions.append(f"{region1} {region2}")
        else:
            if name_in_cell != "0":
                not_found_names.append(name_in_cell)
            
    return {
        "distributor": dist,
        "data": data,
        "not_found_names": list(set(not_found_names)),
        "not_found_regions": not_found_regions
    }


# report_dict = get_report_dict_from_file(
#     filename="Sorrento-39.xlsx",
#     dist="Pharm Luxe",
#     name_cells_template="A(2-#)",
#     region1_cells_template="I(2-#)",
#     region2_cells_template="J(2-#)",
#     sales_cells_template="F(2-#)",
#     client_cells_template="C(2-#)",
#     sheet_index=1
# )


def get_total_report_dict(*file_report_dicts):
    """
    result_dict = {
        "data":{
            "Total": {
                "group1": {
                    "name1": {
                        "Total": 331213,
                        "region1": 1231,
                        "region2": 2145,
                        "region3": 7896,
                        ...
                    },
                },
                "group2": {},
                ...
            },
            "dist1": {},
            "dist2": {},
            ...
        },
        "not_found_names": [],
        "not_found_regions": []
    }
    """

    result_dict = {
        "data": {
            "Total": get_all_names()
        },
        "not_found_names": [],
        "not_found_regions": []
    }

    for file_dict in file_report_dicts:
        dist = file_dict['distributor']
        if dist not in result_dict["data"]:
            result_dict["data"][dist] = get_all_names()

        for group in file_dict['data']:
            for name in file_dict['data'][group]:
                for region in file_dict['data'][group][name]:
                    sales = file_dict['data'][group][name][region]
                    result_dict['data']['Total'][group][name][region] += sales
                    result_dict['data'][dist][group][name][region] += sales
        
        result_dict["not_found_names"] += file_dict["not_found_names"]
        result_dict["not_found_names"] = list(set(result_dict["not_found_names"]))

        result_dict["not_found_regions"] += file_dict["not_found_regions"]
        result_dict["not_found_regions"] = list(set(result_dict["not_found_regions"]))
    
    return result_dict


def create_secondary_report_file(total_report_dict: dict):
    total_report_file = ExcelBook("TotalSecondaryReport.xlsx")
    data = total_report_dict['data']

    regions = [
        'Total',
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
        'Респ. Каракалпакстан',
        'Неизвестный р.'
    ]

    green_color = "F2FFAF"
    yellow_color = "BBFFC6"

    for current_sheet_index in range(0, len(data.keys())):
        dist = list(data.keys())[current_sheet_index]

        if current_sheet_index > 0:
            sheet = total_report_file.book.create_sheet(title=dist)
            total_report_file.book.active = sheet
        else:
            sheet = total_report_file.book.worksheets[0]
            sheet.title = "Total"
        
        total_report_file.book.active = sheet


        # Заголовки

        total_report_file.set_cell_value(
            "A1",
            "Группа",
            sheet_index=current_sheet_index,
            bold=True
        )

        total_report_file.set_column_width("B", 40, sheet_index=current_sheet_index)

        total_report_file.set_cell_value(
            "B1",
            "Наименование",
            sheet_index=current_sheet_index,
            bold=True
        )

        region_columns = ['C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                          'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
                          'Y', 'Z', 'AA', 'AB']
        
        for i in range(0, len(regions)):
            total_report_file.set_cell_value(
                f"{region_columns[i]}1",
                regions[i],
                sheet_index=current_sheet_index,
                center=False,
                bold=True,
                rotate=True
            )

        #  Данные

        group_index = 0
        row = 2

        for group in data[dist].keys():

            color = green_color
            if group_index % 2:
                color = yellow_color

            for name in data[dist][group]:

                total_report_file.set_cell_value(
                    f"A{row}", group, sheet_index=current_sheet_index, fill_color=color
                )
                
                total_report_file.set_cell_value(
                    f"B{row}", name, sheet_index=current_sheet_index, center=False, fill_color=color
                )

                for i in range(0, len(regions)):
                    curr_cell = f"{region_columns[i]}{row}"
                    curr_region = regions[i]
                    curr_sales = int(data[dist][group][name][curr_region])
                    total_report_file.set_cell_value(
                        curr_cell, curr_sales, sheet_index=current_sheet_index
                    )
                
                row += 1

            group_index += 1

        current_sheet_index += 1

    # total_report_file.book.remove(total_report_file.book.worksheets[0])
    total_report_file.book.save("TotalSecondaryReport.xlsx")

# all_reports = get_total_report_dict(report_dict)

# create_secondary_report_file(all_reports)

