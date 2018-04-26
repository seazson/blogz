/**
 * @license Copyright (c) 2003-2017, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.md or http://ckeditor.com/license
 */

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here. For example:
	// config.language = 'fr';
	// config.uiColor = '#AADC6E';
	// %REMOVE_START%
	config.language = 'zh-cn';
	config.uiColor = '#CAE1FF';
	config.height = 500;
	config.toolbarCanCollapse = true;

    //��Ӳ�����������ö��Ÿ���
    config.extraPlugins = 'codesnippet';
    //ʹ��zenburn�Ĵ�����������ʽ PS:zenburnЧ�����Ǻ�ɫ����
    //�����������Ĭ�Ϸ��Ϊdefault
    codeSnippet_theme: 'zenburn';
    config.filebrowserUploadUrl = '/ckupload/'
};
