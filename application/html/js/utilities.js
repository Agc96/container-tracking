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
