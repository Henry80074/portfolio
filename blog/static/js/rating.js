// code for 5 star rating system
// adapted from github repository by lukaszmakinia on 14/10/2020
// accessed on 28/12/2021 from https://github.com/hellopyplane/Star-ratings-with-Django-and-Javascript/tree/main/ratings
// I have adapted the code to work with flask and added additional functionality to display the average rating

// get all the stars
const one = document.getElementById('first')
const two = document.getElementById('second')
const three = document.getElementById('third')
const four = document.getElementById('fourth')
const five = document.getElementById('fifth')
// get the form, confirm-box and csrf token
const form = document.querySelector('.rate-form')
const formContainer = document.getElementById('form-cont')
const confirmBox = document.getElementById('confirm-box')

// collecting data to keep track of post rating without extra database queries
const ratings = document.getElementById('rating_list').value
const user_id = document.getElementById('current_user').value
var ratingsObject = JSON.parse(ratings)
// delete current users rating from list in case of update
delete ratingsObject.user_id

var post = document.getElementById('post_id').value
var critic_avg_rounded = Math.round(document.getElementById('critic_avg').value)
var csrf_token = $('input[name=csrf_token]').attr('value')
// number of additional inputs in form with helpful data
var hiddenInputs = 4
// sets default stars based on average score (rounded to nearest integer)
const defaultChildren = form.children
for (let i=hiddenInputs; i < defaultChildren.length; i++) {
    if(i <= critic_avg_rounded + hiddenInputs) { // add to score to account for additional hidden inputs with values
        defaultChildren[i].classList.add('default-checked')
    } else {
        defaultChildren[i].classList.remove('default-checked')
        }
        }

form.addEventListener('mouseout', (event)=>{
    for (let i=hiddenInputs; i < defaultChildren.length; i++) {
        defaultChildren[i].classList.remove('checked')
        }
    })

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrf_token);
        }
    }
});
const handleStarSelect = (size) => {
    const children = form.children
    for (let i=hiddenInputs; i < children.length; i++) {
        if(i <= size) {
            children[i].classList.add('checked')
        } else {
            children[i].classList.remove('checked')
        }
    }
}

const handleSelect = (selection) => {
    switch(selection){
        case 'first': {
            handleStarSelect(1+hiddenInputs)
            return
        }
        case 'second': {
            handleStarSelect(2+hiddenInputs)
            return
        }
        case 'third': {
            handleStarSelect(3+hiddenInputs)
            return
        }
        case 'fourth': {
            handleStarSelect(4+hiddenInputs)
            return
        }
        case 'fifth': {
            handleStarSelect(5+hiddenInputs)
            return
        }
        default: {
            handleStarSelect(critic_avg_rounded)
        }
    }

}

const getNumericValue = (stringValue) =>{
    let numericValue;
    if (stringValue === 'first') {
        numericValue = 1
    }
    else if (stringValue === 'second') {
        numericValue = 2
    }
    else if (stringValue === 'third') {
        numericValue = 3
    }
    else if (stringValue === 'fourth') {
        numericValue = 4
    }
    else if (stringValue === 'fifth') {
        numericValue = 5
    }
    else {
        numericValue = 0
    }
    return numericValue
}
var globalVal;
if (one) {
    const arr = [one, two, three, four, five]

    arr.forEach(item=> item.addEventListener('mouseover', (event)=>{
        handleSelect(event.target.id)
    }))

    arr.forEach(item=> item.addEventListener('click', (event)=>{
        // value of the rating not numeric
        const val = event.target.id

        let isSubmit = false
        form.addEventListener('submit', e=>{
            e.preventDefault()
            if (isSubmit) {
                return
            }
            isSubmit = true

            // value of the rating translated into numeric
            const val_num = getNumericValue(val)
            // post id
            const post_id = getNumericValue(post)
            // added code for average post rating
            // if user is logged in
            if (user_id != "None") {
                // keeps track of average post rating as user selects a rating
                ratingsObject[user_id] = val_num
                var newAverage = Object.values(ratingsObject)
                Array.prototype.sum = function() {
                    return this.reduce(function(a, b){return a + b;});
                };
                meanScore = Math.round(newAverage.sum() / newAverage.length)

                // shows updated number of default stars that represent overall score across all users
                for (let i=0; i < defaultChildren.length; i++) {
                    if(i <= meanScore+hiddenInputs) { // add to score to account for additional hidden inputs with values
                        defaultChildren[i].classList.add('default-checked')
                    } else {
                        defaultChildren[i].classList.remove('default-checked')
                        }
                        }
            }
            //posts rating to database
            $.ajax({
                type: 'POST',
                url: "/post/"+post+"/rate",
                data: {"val": val_num, "post": post},

                success: function(response){
                    confirmBox.innerHTML = `<h1> You rated the post ${val_num}/5 </h1>`
                },
                error: function(error){
                    confirmBox.innerHTML = `<h1> Please login to rate </h1>`
                }
            })
        })
    }))
}
// end of referenced code