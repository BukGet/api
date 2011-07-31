<div class="logdata">
%for line in reversed(logdata.split('\n')):
  %if len(line) > 0:
  <span><em>{{!line.replace('ve513 bukget_%s: ' % ENV,'</em> ')}}</span>
  %end
%end
</div>
%rebase layout title="Logs"

