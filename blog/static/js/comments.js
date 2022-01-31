
// get the form, value, csrf token
const comment_form = document.querySelector('#comment-form')
const commentConfirmBox = document.getElementById('confirm-box')
var csrf_token = $('input[name=csrf_token]').attr('value')
var comment_submit = document.getElementById('comment_submit_button')
// set csrf token in ajax header
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrf_token);
        }
    }
});
let isSubmit = false
// on submit get comment details
comment_form.addEventListener('submit', e=>{
            var comment_body = document.getElementById('comment_box').value
            var username =  document.getElementById('username').value
            var dateTime = new Date()
            var format = dateTime.toLocaleString("en-UK").replace(",", " -").slice(0, -3)
            e.preventDefault()
            if (isSubmit) {
                return
            }
            isSubmit = true

$.ajax({
    type: 'POST',
    url: "/post/"+post+"/comment",
    data: {"body": comment_body, "username": username, "dateTime": dateTime},
    // if user is authenticated add comment to comments list without need for page refresh
    success: function(response){
        if (username) {
            $('.comment-card-space').prepend(`<div class="comment-card">
                <div class="comment-container">
                    <div class="comment-header">
                        <b>${(username)}</b>
                        <p>${(format)}</p>
                    </div>
                    <div class="comment-body">
                        <p>${(comment_body)}</p>
                    </div>
                </div>
            </div>`)
            document.getElementById('comment_box').value = null
            // request login if not authenticated
        } else {
        commentConfirmBox.innerHTML = `<h1> Please login to comment </h1>`
        }
         },
    error: function(error){
        console.log("e",error)
    }
}
)
isSubmit = false
})