function disp_errors(error) {
	alert(error);
}

document.addEventListener('DOMContentLoaded',() => {
	var x = document.getElementById('err');
	if(x){
		disp_errors(x.innerHTML);
	}
});

function disableBack() { 
	window.history.forward();
 }

window.onpageshow = function(evt) { if (evt.persisted) disableBack() };

window.addEventListener('load', () => {
	disableBack();
	setTimeout(() => {document.querySelector('#loader').style.display = 'none';},1000);
});