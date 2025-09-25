document.addEventListener("DOMContentLoaded", function () {
    const editorArea = document.querySelector(".django-ckeditor-widget");
    if (!editorArea) return;

    // Create Preview Box
    const previewBox = document.createElement("div");
    previewBox.id = "live-preview";
    previewBox.style.border = "1px solid #ddd";
    previewBox.style.padding = "15px";
    previewBox.style.marginTop = "20px";
    previewBox.style.background = "#fafafa";
    previewBox.style.maxHeight = "400px";
    previewBox.style.overflowY = "auto";

    const previewTitle = document.createElement("h3");
    previewTitle.innerText = "Live Preview";
    previewTitle.style.marginBottom = "10px";

    previewBox.appendChild(previewTitle);
    editorArea.parentNode.appendChild(previewBox);

    // Hook CKEditor instance
    for (const instanceName in CKEDITOR.instances) {
        CKEDITOR.instances[instanceName].on("change", function () {
            document.getElementById("live-preview").innerHTML =
                "<h3>Live Preview</h3>" + this.getData();
        });
    }
});
