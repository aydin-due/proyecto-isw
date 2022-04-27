var selectedRow = null

function onFormSubmit() {
    if (validate()) {
        var formData = readFormData();
        if (selectedRow == null)
            insertNewRecord(formData);
        else
            updateRecord(formData);
        resetForm();
    }
}

function readFormData() {
    var formData = {};
    formData["producto"] = document.getElementById("producto").value;
    formData["insumo"] = document.getElementById("insumo").value;
    formData["prov"] = document.getElementById("prov").value;
    return formData;
}

function insertNewRecord(data) {
    var table = document.getElementById("tablaproducto").getElementsByTagName('tbody')[0];
    var newRow = table.insertRow(table.length);
    cell1 = newRow.insertCell(0);
    cell1.innerHTML = data.producto;
    cell2 = newRow.insertCell(1);
    cell2.innerHTML = data.insumo;
    cell3 = newRow.insertCell(2);
    cell3.innerHTML = data.prov;
    cell4 = newRow.insertCell(3);
    cell4.innerHTML = `<a onClick="onEdit(this)">Edit</a>
                       <a onClick="onDelete(this)">Delete</a>`;
}

function resetForm() {
    document.getElementById("producto").value = "";
    document.getElementById("insumo").value = "";
    document.getElementById("prov").value = "";
    selectedRow = null;
}

function onEdit(td) {
    selectedRow = td.parentElement.parentElement;
    document.getElementById("producto").value = selectedRow.cells[0].innerHTML;
    document.getElementById("insumo").value = selectedRow.cells[1].innerHTML;
    document.getElementById("prov").value = selectedRow.cells[2].innerHTML;
}

function updateRecord(formData) {
    selectedRow.cells[0].innerHTML = formData.producto;
    selectedRow.cells[1].innerHTML = formData.producto;
    selectedRow.cells[2].innerHTML = formData.prov;
}

function onDelete(td) {
    if (confirm('Estas seguro que quieres eliminar?')) {
        row = td.parentElement.parentElement;
        document.getElementById("tablaproducto").deleteRow(row.rowIndex);
        resetForm();
    }
}

function validate() {
    isValid = true;
    if (document.getElementById("producto").value == "", document.getElementById("insumo"), document.getElementById("prov").value == "") {
        isValid = false;
        document.getElementById("productoValidationError").classList.remove("hide");
        document.getElementById("insumoValidationError").classList.remove("hide");
        document.getElementById("provValidationError").classList.remove("hide");
    } else {
        isValid = true;
        if (!document.getElementById("productoValidationError").classList.contains("hide"))
            document.getElementById("productoValidationError").classList.add("hide");
        if (!document.getElementById("insumoValidationError").classList.contains("hide"))
            document.getElementById("insumoValidationError").classList.add("hide");
        if (!document.getElementById("provValidationError").classList.contains("hide"))
            document.getElementById("provValidationError").classList.add("hide");
    }
    return isValid;
}