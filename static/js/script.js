const singInLink = document.querySelector('.singIn-link');
const singUpLink = document.querySelector('.singUp-link');

const wrapper = document.querySelector('.wrapper')

singUpLink.addEventListener('click', ()=>{
    wrapper.classList.toggle('active')
})
singInLink.addEventListener('click', ()=>{
    wrapper.classList.toggle('active')
})