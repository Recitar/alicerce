
$("#start").click(function() { 

    $.get("/startSession").done(function(data) {
        $("#start").replaceWith(
            `
            <div id="type_msg">
                <div id="input_msg_write">
                    <textarea id="input_msg" type="text" placeholder="Escreva aqui a sua pergunta"></textarea>
                    <button  id="send_btn" class="btn btn-primary"><i class="fas fa-paper-plane" aria-hidden="true"></i></button>
                </div>
            </div> 
        `
        );

    });
    // $('#startModal').modal('hide');
});


function getCurrentTime(){
    var today = new Date();
    var current_hour = today.getHours();
    var period = " AM";
    if (current_hour > 12){
        current_hour = current_hour - 12;
        period = " PM"
    }
    var time = current_hour + ":" + today.getMinutes() + period; 
    var date_time = `${time}`
    return date_time;
}


function drawUserMessage(raw_text){
    var user_msg_html = `
    <li class="user">
        <div class="chat-img">
            <img alt="Avatar" src="/static/img/user-logo.png">
        </div>
        <div class="chat-body">
            <div class="chat-message">
                <p class="msg-content">${raw_text}</p>
                <div class="text-muted"><small class="message-time">${getCurrentTime()}</span></small>
            </div>
        </div>
    </li>

    `;
    $("#chat-list").append(user_msg_html);  

    // Scroll to bottom
    $('.card-body').animate({scrollTop: $('.card-body')[0].scrollHeight});
}


function drawTypingAction(){
    var typing_html = `
    <li class="bot">
        <div class="chat-img">
            <img alt="Avatar" src="/static/img/bot-logo.png">
        </div>
        <div class="chat-body">
            <div class="chat-message">
                <h5>SucupiraBot</h5>
                    <div id="typing-indicator">
                        <div class="typing-indicator-bubble">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
            </div>
        </div>
    </li>
`;

$("#chat-list").append(typing_html); 
}



$(function() {

    $(document).on("keypress", "textarea#input_msg" , function(e) {
        if(e.which == 13) {
            $('#send_btn').click();
            e.preventDefault();
        }
    });

    $(document).on("click", "button#send_btn" , function() {
        var raw_text = $("#input_msg").val();
        $("#input_msg").val("");
        if (raw_text.trim() != ""){
            drawUserMessage(raw_text);
            drawTypingAction();
            $.get("/answer", { msg: raw_text }).done(function(data) {
                
                var bot_msg_html = data

                $("#typing-indicator").replaceWith(bot_msg_html);
                // scroll to bottom
                $('.card-body').animate({scrollTop: $('.card-body')[0].scrollHeight});

            });
        }
    }); 

    
});


$('.navbar-nav .nav-link').click(function(){
    $('.navbar-nav .nav-link').removeClass('active');
    $(this).addClass('active');
})


$(document).ready(function()
{
    localStorage.openpages = Date.now();
    var onLocalStorageEvent = function(e){
        if(e.key == "openpages"){
            // Emit that you're already available.
            localStorage.page_available = Date.now();
        }
        if(e.key == "page_available"){
            // alert("One more page already open");
            $("#start").replaceWith(
                `
                <div class="alert alert-danger" role="alert">
                    Você não pode iniciar uma nova conversa pois este chat está aberto em mais de uma aba do seu navegador. 
                    Feche as abas que contenham o chatbot aberto e atualize esta página.
                </div>
                `
            );
        }
    };
    window.addEventListener('storage', onLocalStorageEvent, false);
});
