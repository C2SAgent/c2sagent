from tinydb import TinyDB, Query
from typing import Dict, Any, List, Optional

class EnhancedServerToolManager:
    def __init__(self, db_path='enhanced_server_tool_db.json'):
        """初始化增强版数据库"""
        self.db = TinyDB(db_path)
        self.server_table = self.db.table('servers')
    
    def add_tool_to_server(self, server_name: str, tool_data: Dict[str, Any]) -> None:
        """
        添加工具到服务器
        :param server_name: 服务器名称
        :param tool_data: 工具数据，格式为:
            {
                'name': '工具名称',
                'description': '工具描述',
                'inputSchema': {...},  # 输入模式
                'handler': {
                    'url': 'API地址',
                    'method': 'HTTP方法',
                    'key': '认证密钥'
                }
            }
        """
        Server = Query()
        Tool = Query()
        
        # 检查工具是否已存在（基于工具名称）
        existing_server = self.server_table.search(Server.name == server_name)
        
        if existing_server:
            tools = existing_server[0].get('tools', [])
            # 检查工具是否已存在
            tool_exists = any(tool['name'] == tool_data['name'] for tool in tools)
            
            if not tool_exists:
                tools.append(tool_data)
                self.server_table.update({'tools': tools}, Server.name == server_name)
            else:
                # 工具已存在，可以选择更新或忽略（这里选择更新）
                updated_tools = [
                    tool_data if tool['name'] == tool_data['name'] else tool
                    for tool in tools
                ]
                self.server_table.update({'tools': updated_tools}, Server.name == server_name)
        else:
            # 服务器不存在，创建新记录
            self.server_table.insert({'name': server_name, 'tools': [tool_data]})
    
    def get_tools_by_server(self, server_name: str) -> List[Dict[str, Any]]:
        """根据服务器名获取工具列表"""
        Server = Query()
        result = self.server_table.search(Server.name == server_name)
        return result[0]['tools'] if result else []
    
    def get_tool_details(self, server_name: str, tool_name: str) -> Optional[Dict[str, Any]]:
        """获取特定工具的详细信息"""
        tools = self.get_tools_by_server(server_name)
        for tool in tools:
            if tool['name'] == tool_name:
                return tool
        return None
    
    def get_servers_by_tool_name(self, tool_name: str) -> List[str]:
        """根据工具名称获取服务器列表"""
        Server = Query()
        servers = self.server_table.search(Server.tools.any(lambda tool: tool['name'] == tool_name))
        return [server['name'] for server in servers]
    
    def update_tool_handler(self, server_name: str, tool_name: str, new_handler: Dict[str, Any]) -> bool:
        """更新工具的handler信息"""
        Server = Query()
        existing = self.server_table.search(Server.name == server_name)
        
        if existing:
            tools = existing[0].get('tools', [])
            for tool in tools:
                if tool['name'] == tool_name:
                    tool['handler'] = new_handler
                    self.server_table.update({'tools': tools}, Server.name == server_name)
                    return True
        return False
    
    def remove_tool_from_server(self, server_name: str, tool_name: str) -> bool:
        """从服务器移除指定工具"""
        Server = Query()
        existing = self.server_table.search(Server.name == server_name)
        
        if existing:
            tools = existing[0].get('tools', [])
            updated_tools = [tool for tool in tools if tool['name'] != tool_name]
            
            if len(updated_tools) != len(tools):
                self.server_table.update({'tools': updated_tools}, Server.name == server_name)
                return True
        return False
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """获取所有工具信息（跨服务器）"""
        all_servers = self.server_table.all()
        tools = []
        for server in all_servers:
            for tool in server.get('tools', []):
                # 添加服务器信息到工具数据中
                tool_with_server = tool.copy()
                tool_with_server['server_name'] = server['name']
                tools.append(tool_with_server)
        return tools
    
    def search_tools_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """根据关键词搜索工具（搜索名称和描述）"""
        all_tools = self.get_all_tools()
        keyword_lower = keyword.lower()
        return [
            tool for tool in all_tools
            if (keyword_lower in tool['name'].lower() or 
                keyword_lower in tool.get('description', '').lower())
        ]

# 使用示例
if __name__ == "__main__":
    manager = EnhancedServerToolManager()
    
    # 定义工具数据
    tool1 = {
        "name": "tool_calendar_day",
        "description": "When the tool_calendar needs to be invoked: 1. If the user provides a specific date, use that date as the target date; 2. If the user refers to today or yesterday and so on, first obtain the actual current date; 3. Finally convert the date to YYYY-MM-DD format and if the month or day has a leading zero, keep only one digit, not '0M' or '0D' like that before calling tool_calendar.",
        "inputSchema": {
            "type": "object",
            "properties": {"date": {"type": "string"}},
            "required": ["date"]
        },
        "handler": {
            "type": "http_api",
            "url": "http://v.juhe.cn/calendar/day",
            "method": "GET",
            "key": "9c23e0927915f865f02247162db8900d"
        }
    }
    
    tool2 = {
        "name": "tool_weather",
        "description": "When the tool_calendar needs to be invoked: 1. You just need to provide the city name; 2. The tool_weather will return the future weather forecast for the next 5 days.",
        "inputSchema": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"]
        },
        "handler": {
            "type": "http_api",
            "url": "http://apis.juhe.cn/simpleWeather/query",
            "method": "GET",
            "key": "5e7d8a7d2682ab0d42306237666af91e"
        }
    }
    
    # 添加工具到服务器
    manager.add_tool_to_server('AI-Server-1', tool1)
    manager.add_tool_to_server('AI-Server-1', tool2)
    manager.add_tool_to_server('AI-Server-2', tool1)  # 同样的工具可以存在于不同服务器
    
    # 查询示例
    print("AI-Server-1 的所有工具:")
    for tool in manager.get_tools_by_server('AI-Server-1'):
        print(f"- {tool['name']}: {tool['description']}")
    
    print("\nImageProcessor 工具的详细信息:")
    print(manager.get_tool_details('AI-Server-1', 'ImageProcessor'))
    
    print("\n所有包含 ImageProcessor 的服务器:")
    print(manager.get_servers_by_tool_name('ImageProcessor'))
    
    # 更新工具handler示例
    new_handler = {
        'url': 'https://api.new-example.com/v2/image',
        'method': 'PUT',
        'key': 'new-img-secret-2023'
    }
    manager.update_tool_handler('AI-Server-1', 'ImageProcessor', new_handler)
    
    print("\n更新后的 ImageProcessor 信息:")
    print(manager.get_tool_details('AI-Server-1', 'ImageProcessor'))
    
    # 搜索功能示例
    print("\n搜索包含 'text' 的工具:")
    for tool in manager.search_tools_by_keyword('text'):
        print(f"- {tool['name']} (在服务器 {tool['server_name']}): {tool['description']}")