let taskId = null;

function toggleDark() {
    document.body.classList.toggle("dark");
}

function startDownload() {
    const url = document.getElementById("url").value;
    const quality = document.getElementById("quality").value;

    fetch("/download", {
        method: "POST",
        body: new URLSearchParams({ url, quality })
    })
    .then(res => res.json())
    .then(data => {
        taskId = data.task_id;
        document.getElementById("status").innerText = "Downloading...";
        checkProgress();
    });
}

function checkProgress() {
    fetch(`/progress/${taskId}`)
    .then(res => res.json())
    .then(data => {
        let percent = parseInt(data.progress);
        document.getElementById("progress-bar").style.width = percent + "%";

        if (percent < 100) {
            setTimeout(checkProgress, 1000);
        } else {
            document.getElementById("status").innerText = "Download ready";
            window.location.href = `/file/${taskId}`;
        }
    });
}
