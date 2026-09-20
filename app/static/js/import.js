document.addEventListener("DOMContentLoaded", () => {
    const importBtn = document.getElementById("import-btn");
    const resultsDiv = document.getElementById("results");

    importBtn.addEventListener("click", async () => {
        importBtn.disabled = true;
        resultsDiv.innerText = "Importing data, please wait...";

        try {
            const response = await fetch('/api/projects', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            resultsDiv.innerText = `Status: ${data.status} | Added: ${data.added}`;
            
        } catch (error) {
            resultsDiv.innerText = `Error during import: ${error.message}`;
        } finally {
            importBtn.disabled = false;
        }
    });
});