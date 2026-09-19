document.addEventListener("DOMContentLoaded", () => {

    const importButton =
        document.getElementById("import-projects-btn");

    const deleteButton =
        document.getElementById("delete-projects-btn");

    const analyzeButton =
        document.getElementById("analyze-projects-btn");

    const addedElement =
        document.getElementById("projects-added");

    const updatedElement =
        document.getElementById("projects-updated");

    const deletedElement =
        document.getElementById("projects-deleted");

    const creationDateElement =
        document.getElementById("database-creation-date");

    const statusElement =
        document.getElementById("import-status");


    async function importProjects() {

        importButton.disabled = true;

        statusElement.textContent =
            "Importing NASA projects...";

        try {

            const response = await fetch(
                "/api/projects",
                {
                    method: "POST"
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.message || "Import failed."
                );
            }

            const dbUpdate = data.db_update;

            addedElement.textContent =
                dbUpdate.projects_added;

            updatedElement.textContent =
                dbUpdate.projects_updated;

            deletedElement.textContent =
                dbUpdate.projects_deleted;

            creationDateElement.textContent =
                dbUpdate.database_creation_date || "—";

            statusElement.textContent =
                "Import completed successfully.";

            importButton.hidden = true;
            analyzeButton.hidden = false;

        } catch (error) {

            console.error(error);

            statusElement.textContent =
                `Import error: ${error.message}`;

            importButton.disabled = false;
        }
    }


    async function deleteProjects() {

        const confirmed = window.confirm(
            "Are you sure you want to delete all NASA projects?"
        );

        if (!confirmed) {
            return;
        }

        deleteButton.disabled = true;

        statusElement.textContent =
            "Deleting NASA projects...";

        try {

            const response = await fetch(
                "/api/projects",
                {
                    method: "DELETE"
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.message || "Delete failed."
                );
            }

            /*
             * The backend has successfully deleted the
             * project dataset.
             *
             * Return to the import page so its state is
             * reconstructed from the database.
             */
            window.location.href = "/";

        } catch (error) {

            console.error(error);

            statusElement.textContent =
                `Delete error: ${error.message}`;

            deleteButton.disabled = false;
        }
    }


    function analyzeProjects() {
        window.location.href = "/projects";
    }


    importButton.addEventListener(
        "click",
        importProjects
    );

    deleteButton.addEventListener(
        "click",
        deleteProjects
    );

    analyzeButton.addEventListener(
        "click",
        analyzeProjects
    );

});