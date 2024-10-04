function submitData() {
    const userID = document.getElementById("userID").value;
    const systemMessage = document.getElementById("systemMessage").value;
    const llm_model = document.getElementById("llm_model").value;
    const chatMessage = document.getElementById("chatInput").value;
    const pdfFiles = document.getElementById("fileUpload").files;

    const formData = new FormData();
    formData.append("userID", userID);  // New field for user ID
    formData.append("systemMessage", systemMessage);
    formData.append("chatMessage", chatMessage);
    formData.append("llm_model", llm_model);
    // Append each file to form data
    for (let i = 0; i < pdfFiles.length; i++) {
        formData.append("fileUpload", pdfFiles[i]);
    }

    // Display the human message in the message log with userID
    appendMessage(chatMessage, true); // Passing true since this is a user message

    fetch("/submit", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Display the AI response in the message log
        appendMessage(data.response, false); // Passing false for AI response

        // Clear the input field after submitting
        document.getElementById("chatInput").value = "";

        // Check the length of the message log and disable the tone selection if needed
        const messageLog = document.getElementById("messageLog");
        if (messageLog.childElementCount > 1) {
            document.getElementById("systemMessage").disabled = true;
            document.getElementById("llm_model").disabled = true;
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

function appendMessage(message, isUser) {
    const messageLog = document.getElementById("messageLog");
    let userID = document.getElementById("userID").value;

    // Determine if the message is from the user or AI
    if (isUser) {
        message = userID + ": " + message; // Show userID instead of "You"
    } else {
        message = "AI: " + message;
    }

    // Prepend the new message to the message log
    messageLog.innerHTML = "<div>" + message + "</div>" + messageLog.innerHTML;

    // Scroll to the top of the message log to show the latest message
    messageLog.scrollTop = messageLog.scrollHeight;
}

const fileUpload = document.getElementById('fileUpload');
const fileList = document.getElementById('fileList');

fileUpload.addEventListener('change', (event) => {
    const files = event.target.files;
    fileList.innerHTML = '';  // Clear previous files

    Array.from(files).forEach(file => {
        const listItem = document.createElement('li');
        const fileName = document.createElement('span');
        fileName.textContent = file.name;

        const cancelIcon = document.createElement('span');
        cancelIcon.textContent = '❌'; // Cancel icon
        cancelIcon.className = 'cancel-icon';
        cancelIcon.onclick = () => {
            listItem.remove();  // Remove the file from the list
        };

        listItem.appendChild(fileName);
        listItem.appendChild(cancelIcon);
        fileList.appendChild(listItem);
    });
});
