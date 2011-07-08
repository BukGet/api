            <div class="package">
                <div class="header">
                    <div class="wrapper"> 
                        <div class="info">
                            <div class="authors">
                            {foreach $authors as $i => $author}
                                {if $author eq $maintainer}<strong>{$author}</strong>{else}{$author}{/if}
                                {if $author@last}{else}, {/if}
                            {foreachelse}
                                <strong>{$maintainer}</strong></div>
                            {/foreach}
                            </div>
                        </div>
                        
                        <h1>{$name}</h1>
                        <div class="desc">{$description}</div>
                    </div>
                </div>
                
                <div class="meta rounded-five">pkg install {$name}{foreach $versions as $i => $v}<span class="hidden v{$v.version_u}">@{$v.version}</span>{/foreach}</div>
                
                <div class="wrapper">
                    <div class="versions grid_10">
                        <h2 class="top-rounded-five">Versions</h2>
                        <ul>
                        {foreach $versions as $i => $v}
                            <li><a href="#/package/{$name}/{$v.version_u}" id="v" version="{$v.version_u}" class="{$v.version_u}">{$v.version}</a></li>
                        {foreachelse}
                            <li>No versions found</li>
                        {/foreach}
                        </ul>
                    </div>
                    
                    <div class="info">
                    {foreach $versions as $i => $v}
                        <div class="v{$v.version_u} version">{$required=$v.required_dependencies}{$optional=$v.optional_dependencies}{$engines=$v.engines}
                            <a href="{$v.url}" class="buttons cancel download">Download {$v.version}</a>
                            
                            <div class="item"><span>Works With:</span> {foreach $engines as $i => $e}{$e.name} ({$e.min} - {$e.max}){if $e@last}{else}, {/if}{/foreach}</div>
                            <div class="item"><span>Branch:</span> {$v.branch}</div>
                            <div class="item"><span>Checksum:</span> {$v.checksum}</div>
                            <div class="item"><span>Required Dependencies:</span> {foreach $required as $i => $r}{$r}{if $r@last}{else}, {/if}{foreachelse}None{/foreach}</div>
                            <div class="item"><span>Optional:</span> {foreach $optional as $i => $o}{$o}{if $o@last}{else}, {/if}{foreachelse}None{/foreach}</div>
                        </div>
                    {foreachelse}
                        <div class="info show grid_10">
                            Nothing found.
                        </div>
                    {/foreach}
                    
                        <div class="comments">
                            <div id="disqus_thread"></div>
                            <script type="text/javascript">
                                var disqus_shortname = 'bukget';
                                var disqus_identifier = '{$name}';
                                var disqus_url = 'http://bukget.org/repo/#!/package/{$name}';
                                var disqus_title = '{$name} Comments';
                                (function() {
                                    var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
                                    dsq.src = 'http://' + disqus_shortname + '.disqus.com/embed.js';
                                    (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
                                })();
                            </script>
                            <noscript>Please enable JavaScript to view the repository.</noscript>
                        </div>
                    </div>
                    <div class="clear"></div>
                </div>
            </div>