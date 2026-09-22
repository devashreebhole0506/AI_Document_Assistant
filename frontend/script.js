const API_BASE_URL = "";


/* =====================================================
   SESSION
===================================================== */

let sessionId =
    localStorage.getItem(
        "chat_session_id"
    );


if (!sessionId) {

    sessionId =
        "session_" +
        crypto.randomUUID();

    localStorage.setItem(
        "chat_session_id",
        sessionId
    );
}


/* =====================================================
   ELEMENTS
===================================================== */

const chatMessages =
    document.getElementById(
        "chatMessages"
    );


const messageInput =
    document.getElementById(
        "messageInput"
    );


const sendButton =
    document.getElementById(
        "sendButton"
    );


const typingIndicator =
    document.getElementById(
        "typingIndicator"
    );


const documentInput =
    document.getElementById(
        "documentInput"
    );


const uploadButton =
    document.getElementById(
        "uploadButton"
    );


const uploadStatus =
    document.getElementById(
        "uploadStatus"
    );


const documentList =
    document.getElementById(
        "documentList"
    );


/* =====================================================
   SCROLL CHAT TO BOTTOM
===================================================== */

function scrollChatToBottom(
    smooth = true
) {

    if (!chatMessages) {
        return;
    }


    chatMessages.scrollTo({

        top:
            chatMessages.scrollHeight,

        behavior:
            smooth
                ? "smooth"
                : "auto"
    });
}


/* =====================================================
   ADD CHAT MESSAGE
===================================================== */

function addMessage(
    role,
    text,
    sources = []
) {

    const message =
        document.createElement(
            "div"
        );


    message.className =
        `message ${role}`;


    const content =
        document.createElement(
            "div"
        );


    content.className =
        "message-content";


    const title =
        document.createElement(
            "strong"
        );


    title.textContent =
        role === "user"
            ? "You"
            : "AI Assistant";


    const paragraph =
        document.createElement(
            "p"
        );


    paragraph.textContent =
        text;


    content.appendChild(
        title
    );


    content.appendChild(
        paragraph
    );


    /* =========================================
       SOURCES
    ========================================= */

    if (
        role === "assistant" &&
        sources.length > 0
    ) {

        const sourceBox =
            document.createElement(
                "div"
            );


        sourceBox.className =
            "sources";


        const sourceTitle =
            document.createElement(
                "strong"
            );


        sourceTitle.textContent =
            "Sources:";


        sourceBox.appendChild(
            sourceTitle
        );


        sources.forEach(
            source => {

                const sourceItem =
                    document.createElement(
                        "div"
                    );


                const pageText =
                    source.page
                        ? ` - Page ${source.page}`
                        : "";


                sourceItem.textContent =
                    `${source.document}${pageText}`;


                sourceBox.appendChild(
                    sourceItem
                );

            }
        );


        content.appendChild(
            sourceBox
        );
    }


    message.appendChild(
        content
    );


    chatMessages.appendChild(
        message
    );


    /* =========================================
       SCROLL AFTER MESSAGE IS RENDERED
    ========================================= */

    requestAnimationFrame(
        () => {

            scrollChatToBottom(
                true
            );

        }
    );
}


/* =====================================================
   SEND MESSAGE
===================================================== */

async function sendMessage() {

    const message =
        messageInput.value.trim();


    if (!message) {

        return;
    }


    /* Add user's question */

    addMessage(
        "user",
        message
    );


    /* Clear input */

    messageInput.value = "";


    /* Disable button */

    sendButton.disabled = true;


    /* Show typing */

    typingIndicator.classList.remove(
        "hidden"
    );


    /* Scroll */

    scrollChatToBottom(
        true
    );


    try {

        const response =
            await fetch(
                `${API_BASE_URL}/chat`,
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify(
                            {

                                session_id:
                                    sessionId,

                                message:
                                    message

                            }
                        )

                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Chat request failed."
            );

        }


        /* Add AI response */

        addMessage(
            "assistant",
            data.response,
            data.sources || []
        );

    }

    catch (error) {

        addMessage(
            "assistant",
            `Error: ${error.message}`
        );

    }

    finally {

        sendButton.disabled =
            false;


        typingIndicator.classList.add(
            "hidden"
        );


        messageInput.focus();


        scrollChatToBottom(
            true
        );
    }
}


/* =====================================================
   SEND BUTTON
===================================================== */

sendButton.addEventListener(
    "click",
    sendMessage
);


/* =====================================================
   ENTER KEY
===================================================== */

messageInput.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();

        }

    }
);


/* =====================================================
   AUTO RESIZE TEXTAREA
===================================================== */

messageInput.addEventListener(
    "input",
    () => {

        messageInput.style.height =
            "auto";


        messageInput.style.height =
            Math.min(
                messageInput.scrollHeight,
                140
            ) + "px";

    }
);


/* =====================================================
   DOCUMENT UPLOAD
===================================================== */

uploadButton.addEventListener(
    "click",
    async () => {

        const file =
            documentInput.files[0];


        if (!file) {

            uploadStatus.textContent =
                "Please select a PDF or TXT file.";

            return;
        }


        const formData =
            new FormData();


        formData.append(
            "file",
            file
        );


        uploadButton.disabled =
            true;


        uploadStatus.textContent =
            "Uploading and processing...";


        try {

            const response =
                await fetch(
                    `${API_BASE_URL}/documents/upload`,
                    {

                        method: "POST",

                        body: formData

                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Upload failed."
                );

            }


            uploadStatus.textContent =
                `Processed successfully: ${data.chunks} chunks`;


            const emptyMessage =
                document.querySelector(
                    ".empty-message"
                );


            if (emptyMessage) {

                emptyMessage.remove();

            }


            const documentItem =
                document.createElement(
                    "div"
                );


            documentItem.className =
                "document-item";


            documentItem.textContent =
                `${data.filename} (${data.chunks} chunks)`;


            documentList.appendChild(
                documentItem
            );


            documentInput.value = "";


        }

        catch (error) {

            uploadStatus.textContent =
                `Error: ${error.message}`;

        }

        finally {

            uploadButton.disabled =
                false;

        }

    }
);