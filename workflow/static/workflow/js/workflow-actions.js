function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');

        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

function loadDepartments() {
    fetch("/api/departments/")
        .then(res => res.json())
        .then(data => {
            const select = document.getElementById("routeDepartmentSelect");

            // reset dropdown
            select.innerHTML = '<option value="">Select Department</option>';

            data.forEach(dept => {
                const option = document.createElement("option");
                option.value = dept.id;
                option.textContent = dept.name;
                select.appendChild(option);
            });
        })
        .catch(err => {
            console.error("Department load failed:", err);
        });
}


async function submitRoute() {

    const documentId = document.getElementById("routeDocumentId").value;
    const departmentId = document.getElementById("routeDepartmentSelect").value;
    const remarks = document.getElementById("routeRemarks").value;

    let formData = new FormData();
    formData.append("document_id", documentId);
    formData.append("to_department_id", departmentId);
    formData.append("remarks", remarks);

    try {
        const response = await fetch("/submit-route/", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken
            },
            body: formData
        });

        const data = await response.json();

        if (data.success) {

            // close modal
            const modalEl = document.getElementById("routeModal");
            const modal = bootstrap.Modal.getInstance(modalEl);
            modal.hide();

            alert(data.message || "Routed successfully");

            // optional: remove row from table
            const row = document.querySelector(`[data-doc-id="${documentId}"]`)?.closest("tr");
            if (row) row.remove();

        } else {
            alert(data.message || "Route failed");
        }

    } catch (err) {
        console.error("Submit route error:", err);
        alert("Network error occurred");
    }
}

document.addEventListener("DOMContentLoaded", () => {

    const buttons = document.querySelectorAll(".workflow-action");

    buttons.forEach(button => {

        button.addEventListener("click", async () => {

            const url = button.dataset.url;
            const action = button.dataset.action;

            let formData = new FormData();

            try {

                const response = await fetch(url, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrftoken
                    },
                    body: formData
                });

                const data = await response.json();

                if (data.success) {

                    const row = button.closest("tr");

                    // UI behavior based on action
                    if (
                        action === "ack" ||
                        action === "reject" ||
                        action === "route"
                    ) {
                        row.remove();
                    }

                    alert(data.message || "Success");

                } else {
                    alert(data.message || "Action failed");
                }

            } catch (error) {
                console.error("Workflow error:", error);
                alert("Network error occurred");
            }

        });

    });

    document.querySelectorAll(".route-action").forEach(button => {
        button.addEventListener("click", () => {
            const docId = button.dataset.docId;

            document.getElementById("routeDocumentId").value = docId;

            const modal = new bootstrap.Modal(
                document.getElementById("routeModal")
            );

            modal.show();
        });
    });

    loadDepartments();

    document.getElementById("submitRouteBtn").addEventListener("click", submitRoute);

});