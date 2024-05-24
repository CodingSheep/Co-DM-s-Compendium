import discord

class InfoCard:
    def __init__(self, data):
        self.type = list(data.keys())[0]
        self.data = self.get_data(data)

    def get_data(self, data):
        type = list(data.keys())[0]
        match type:
            case 'npcs':
                return {
                    'Name': data['npcs'][0][1],
                    'Occupation': data['npcs'][0][2],
                    'Description': data['npcs'][0][3],
                    'Location': data['npcs'][0][4]
                }
            case 'locations':
                pass
            case 'cities':
                pass
            case 'items':
                pass
            case default:
                # This case should never happen but who knows
                return {}
    
    def info(self):
        embed = discord.Embed(title=self.data['Name'], description=self.data['Description'])
        match self.type:
            case 'npcs':
                embed.add_field(name='Occupation', value=self.data['Occupation'])
                embed.add_field(name='Location', value=self.data['Location'])
            case default:
                pass
        return embed