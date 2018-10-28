import click

from yify import subs
from yify.subs import OrderBy
from yify.yify import search_subtitles


def print_help_msg(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))

@click.command()
@click.option('-d', '--dir', help='Create a json from dir.')
@click.option('-o', '--sort',default='fromto', help='Index the Subtitle by [fromto(DEFAULT), pk,from,to, all] may produce variations!!!')
@click.option('-a', '--all', is_flag=True, help='Create a json to all folders.',)
def handle(dir, sort, all):
    '''
     Translate from subtitle!
     Please pick a folder you have imported and see the generated file
     Or check its log in the md file
     '''
    if dir is None and all is False:
        print_help_msg(handle)
        return
    if all:
        folders = subs.get_options()
        while folders:
            subs.create_json_from_folder(folders.pop(), OrderBy.getsort(sort))
    else:
        subs.create_json_from_folder(dir, OrderBy.getsort(sort))


@click.command(name="yify")
@click.option('--count', default=3, help='Max Limit the result or DDOS attack your call.')
@click.argument('movie')
def main(movie, count):
    '''
    Search movie names to insert or just mess with the data
    '''
    search_subtitles(movie, count)


@click.group(name="lengua")
def lengua():
    pass


lengua.add_command(main)
lengua.add_command(handle)

if __name__ == '__main__':
    lengua()
