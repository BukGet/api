            <div class="wrapper">
                <div class="side-bar">
                    <input type="search" results="5" class="s" placeholder="Search.." class="rounded-three">
                </div>
                
                <div class="pack-list">
                    {foreach $packages as $i => $pack}
                    <div class="pack">
                        <div class="categories">
                            {$categories=$pack.categories}
                            {foreach $categories as $i => $category}
                                {if $category eq "ADMIN"}
                                    {$category="ADMN"}
                                {/if}
                                <a href="#/category/{$category}" class="buttons small">{$category}</a>
                            {foreachelse}
                                ...
                            {/foreach}
                        </div>
                        <span class="name" onClick="window.location = '#/package/{$pack.name}';">{$pack.name}</span>
                        <div class="description" onClick="window.location = '#/package/{$pack.name}';">
                            <span class="maintainer">Maintained by: {$pack.maintainer}</span>
                            <span class="desc">{$pack.description}</span>
                        </div>
                    </div>
                    {foreachelse}
                    <div class="error">
                        <span class="description">No Results</span>
                    </div>
                    {/foreach}
                </div>
                
                {if $chunkLength < 0 || $chunkLength eq 0}{else}
                <ol class="pagination">
                    {foreach $chunks as $i => $chunk}
                    <li{if $i eq $page} class="on"{/if}><a href="{if $i eq 0}{$path}{else}{$path}/page/{$i}{/if}" title="Page {$i}">Page {$i}</a></li>
                    {/foreach}
                </ol>
                {/if}
            </div>