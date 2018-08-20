(function(){
  var jquery_version = '2.1.4';
  var site_url = 'http://127.0.0.1/';
  var static_url = site_url + 'static/';
  //书签在网站中将要寻找的图像的最小宽度和最小高度
  var min_width = 100;
  var min_height = 100;

  function bookmarklet(msg) {
    // 加载 bookmarklet.css 样式表，使用随机数字作为参数来避免浏览器的缓存
    var css = jQuery('<link>');
    css.attr({
      rel: 'stylesheet',
      type: 'text/css',
      href: static_url + 'css/bookmarklet.css?r=' + Math.floor(Math.random()*99999999999999999999)
    });
    jQuery('head').append(css);

    // 加载 HTML
    box_html = '<div id="bookmarklet"><a href="#" id="close">&times;</a><h1>选择要收藏的图片</h1><div class="images"></div></div>';
    jQuery('body').append(box_html);

	  // 如果点击就关闭提示
	  jQuery('#bookmarklet #close').click(function(){
      jQuery('#bookmarklet').remove();
	  });

    // 找到图片并展示
    jQuery.each(jQuery('img[src$=".gif"], img[src$=".jpg"], img[src$=".png"], img[src$=".bmp"]'), function(index, image) {
      if (jQuery(image).width() >= min_width && jQuery(image).height() >= min_height)
      {
        image_url = jQuery(image).attr('src');
        jQuery('#bookmarklet .images').append('<a href="#"><img src="'+ image_url +'" /></a>');
      }
    });

    // 当图片被选中，打开图片的地址
    jQuery('#bookmarklet .images a').click(function(e){
      selected_image = jQuery(this).children('img').attr('src');
      // 隐藏收藏按钮
      jQuery('#bookmarklet').hide();
      // 打开收藏的超链接
      window.open(site_url +'images/create/?url='
                  + encodeURIComponent(selected_image)
                  + '&title=' + encodeURIComponent(jQuery('title').text()),
                  '_blank');
    });

  };
  // Check if jQuery is loaded
  if(typeof window.jQuery != 'undefined') {
    bookmarklet();
  } else {
    // Check for conflicts
    var conflict = typeof window.$ != 'undefined';
    // Create the script and point to Google API
    var script = document.createElement('script');
    script.setAttribute('src','http://ajax.googleapis.com/ajax/libs/jquery/' + jquery_version + '/jquery.min.js');
    // Add the script to the 'head' for processing
    document.getElementsByTagName('head')[0].appendChild(script);
    // Create a way to wait until script loading
    var attempts = 15;
    (function(){
      // Check again if jQuery is undefined
      if(typeof window.jQuery == 'undefined') {
        if(--attempts > 0) {
          // Calls himself in a few milliseconds
          window.setTimeout(arguments.callee, 250)
        } else {
          // Too much attempts to load, send error
          alert('An error ocurred while loading jQuery')
        }
      } else {
          bookmarklet();
      }
    })();
  }

})()
