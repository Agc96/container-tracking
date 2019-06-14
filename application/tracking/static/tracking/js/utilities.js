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

});

/* Métodos auxiliares */
var Utilities = {
	showMessage: function(messageType, messageContent, messageIcon, messageTitle) {
		iziToast.show({
			class: 'iziToast-' + (messageType || 'default'),
			title: (messageTitle || ''),
			message: (messageContent || ''),
			animateInside: false,
			position: 'topRight',
			progressBar: false,
			icon: (messageIcon || ''),
			timeout: 3200,
			transitionIn: 'fadeInLeft',
			transitionOut: 'fadeOut',
			transitionInMobile: 'fadeIn',
			transitionOutMobile: 'fadeOut'
		});
	},
	showErrorMessage: function(messageContent) {
		Utilities.showMessage('danger', messageContent, 'icon-ban', 'Error');
	},
	showSuccessMessage: function(messageContent) {
		Utilities.showMessage('success', messageContent, 'icon-check', 'Éxito');
	}
}
