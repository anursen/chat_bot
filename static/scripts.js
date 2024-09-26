function submitData() {
    const systemMessage = document.getElementById("systemMessage").value;
    const llm_model  = document.getElementById("llm_model").value;
    const chatMessage = document.getElementById("chatInput").value;
    const pdfFile = document.getElementById("pdfFile").files[0];

    const formData = new FormData();
    formData.append("systemMessage", systemMessage);
    formData.append("chatMessage", chatMessage);
    formData.append("llm_model", llm_model);
    if (pdfFile) {
        formData.append("pdfFile", pdfFile);
    }

    // Display the human message in the message log
    appendMessage("You: " + chatMessage);

    fetch("/submit", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Display the AI response in the message log
        appendMessage("AI: " + data.response);
        // Clear the input field after submitting
        document.getElementById("chatInput").value = "";
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

function appendMessage(message) {
    const messageLog = document.getElementById("messageLog");
    // Prepend the new message to the message log
    messageLog.innerHTML = "<div>" + message + "</div>" + messageLog.innerHTML;
    // Scroll to the top of the message log to show the latest message
    messageLog.scrollTop = messageLog.scrollHeight; // Change this line
}
