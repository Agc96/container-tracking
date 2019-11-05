jQuery(document).ready(function ($) {

	/* Selects con placeholders */

	$('select').each(selectPlaceholder).change(selectPlaceholder);

	function selectPlaceholder() {
		if (this.value === '') {
			$(this).addClass('placeholder');
		} else {
			$(this).removeClass('placeholder');
		}
	}

	$('[type=reset]').click(function () {
		$(this).parents('form').find('select').addClass('placeholder');
	});

	/* Inputs tipo fecha */

	if ($.fn.datepicker) {
		$('.date-input').datepicker({
			dateFormat: 'dd/mm/yy',
			monthNames: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Setiembre',
						'Octubre', 'Noviembre', 'Diciembre'],
			monthNamesShort: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Set', 'Oct', 'Nov', 'Dic'],
			dayNamesMin: ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'],
			prevText: 'Anterior',
			nextText: 'Siguiente',
			showOtherMonths: true,
			selectOtherMonths: true
		});
	}

});

/* Métodos auxiliares */

function showMessage(type, content, icon, title) {
	iziToast.show({
		class: 'iziToast-' + (type || 'default'),
		title: (title || ''),
		message: (content || ''),
		animateInside: false,
		position: 'topRight',
		progressBar: false,
		icon: (icon || ''),
		timeout: 3200,
		transitionIn: 'fadeInLeft',
		transitionOut: 'fadeOut',
		transitionInMobile: 'fadeIn',
		transitionOutMobile: 'fadeOut'
	});
}

function showErrorMessage(content) {
	showMessage('danger', content, 'icon-ban', 'Error');
}

function showSuccessMessage(content) {
	showMessage('success', content, 'icon-check', 'Éxito');
}
